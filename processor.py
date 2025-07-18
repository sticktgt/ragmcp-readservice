import os
from pathlib import Path
from typing import List, Optional, Tuple
from .output.saver import save_doc_text, save_metadata_entry
from .loaders.document_loader import load_document
from .sources.local import LocalFileSource
from .sources.s3 import S3FileSource
from .config import CONFIG
from .utils.splitters import split_documents_lazy
from .utils.logger import get_logger
import traceback
from .utils.embedding import get_embedding_function
from pymilvus import connections
from langchain_core.documents import Document
from .utils.milvus_store import MilvusStore

from itertools import tee
from .utils.search_milvus import search_main

logger = get_logger()

def is_already_uploaded(hashcode: str, store: MilvusStore) -> Tuple[bool, Optional[str]]:
    return store.document_exists(hashcode)


def handle_file(file_id: str, content: Optional[bytes], meta: dict,
                store: MilvusStore, doc_index: int,
                err_log, output_dir: str, meta_path: str) -> int:
    """Handle a single file: load, split, embed, and store."""
    file_parts = 0
    try:
        logger.info(f"Processing: {file_id}")
        docs, load_error, source_hash = load_document(file_id, content)
        if load_error:
            logger.error(f"[LOAD ERROR] {file_id}: {load_error}")
            err_log.write(f"[LOAD ERROR] {file_id}: {load_error}\n")
            return 0

        if CONFIG.get("debug", True):
            docs = list(docs)  # Materialize the iterator once for debugging
            file_parts = len(docs)

        if source_hash:
            # Check if the document already exists in Milvus by hashcode
            is_exists, exists_error = is_already_uploaded(source_hash, store)
            if exists_error:
                logger.error(f"[CHECK ERROR] {file_id}: {exists_error}")
                err_log.write(f"[CHECK ERROR] {file_id}: {exists_error}\n")
                return 0            
            if is_exists:
                # if the document already exists in Milvus by hashcode
                logger.info(f"[SKIP] {file_id} (hash exists)")
                if CONFIG.get("delete_old_vectors", False): # for a test purpose only!!
                    store.delete_by_hash(source_hash) # for a test purpose only!!
                return 0
            source = meta.get("source")
            if source:
                # Search for existing documents by the same source
                edocs, edocs_error = store.get_distinct_filenames_by_source(source)
                if edocs_error:
                    logger.error(f"[SEARCH ERROR] {file_id}: {edocs_error}")
                    err_log.write(f"[SEARCH ERROR] {file_id}: {edocs_error}\n")
                    return 0
                logger.info(f"[SEARCH] found {len(edocs)} existing documents with source: {source}")
                if CONFIG.get("debug", False):
                    if len(edocs) > 0:
                        logger.debug(f"[SEARCH] {edocs}")

        ext = Path(file_id).suffix.lower()
        split_docs, split_error = split_documents_lazy(docs, file_ext=ext, config=CONFIG["splitters"])
        if split_error:
            logger.error(f"[SPLIT ERROR] {file_id}: {split_error}")
            err_log.write(f"[SPLIT ERROR] {file_id}: {split_error}\n")
            return 0

        chunk_docs = []
        for split_doc in split_docs:
            split_doc.metadata.update(meta)
            chunk_docs.append(split_doc)

        store_error = store.add_documents(chunk_docs)
        if store_error:
            logger.error(f"[STORE ERROR] {file_id}: {store_error}")
            err_log.write(f"[STORE ERROR] {file_id}: {store_error}\n")
            if source_hash:
                store.delete_by_hash(source_hash)
            return -1

        if CONFIG.get("debug", True):
            if source_hash:
                store.retrieve_vectors_by_hashcode(source_hash)
                # store.print_by_hashcode(source_hash)

        for doc in chunk_docs:
            if CONFIG.get("debug", True):
                save_doc_text(doc, doc_index, output_dir)
            save_metadata_entry(doc, doc_index, meta_path)
            doc_index += 1

        if CONFIG.get("debug", True):
            logger.info(f"Processed {file_id}: {file_parts} parts, {len(chunk_docs)} chunks")
        return len(chunk_docs)

    except Exception as e:
        logger.error(f"[CRITICAL ERROR] {file_id}: {e}")
        err_log.write(f"[CRITICAL ERROR] {file_id}: {e}\n")
        logger.debug(traceback.format_exc())
        return -1

def process_streaming():
    doc_index = 0
    docs_count = 0
    store = None
    try:
        output_dir = CONFIG["output_dir"]
        os.makedirs(output_dir, exist_ok=True)
        meta_path = os.path.join(output_dir, "metadata.jsonl")
        error_path = os.path.join(output_dir, "errors.log")

        embedding_function = get_embedding_function(CONFIG["embedding"])
        store = MilvusStore(CONFIG["milvus"], embedding_function=embedding_function)

        sources = []
        if CONFIG.get("use_local"):
            sources.append(LocalFileSource(CONFIG["local_path"], CONFIG["file_types"]))
        if CONFIG.get("use_s3"):
            sources.append(S3FileSource(CONFIG, CONFIG["file_types"]))

        with open(error_path, "w", encoding="utf-8") as err_log:
            for source in sources:
                logger.info(f"Processing source: {source.__class__.__name__}")
                for file_id, content, meta, source_error in source.iterate_files():
                    if source_error:
                        logger.error(f"[SOURCE ERROR] {file_id}: {source_error}")
                        err_log.write(f"[SOURCE ERROR] {file_id}: {source_error}\n")
                        continue

                    result = handle_file(file_id, content, meta, store, doc_index, err_log, output_dir, meta_path)
                    if result < 0:
                        logger.critical(f"[FATAL] Aborting due to error in file: {file_id}")
                        return
                    elif result > 0:
                        doc_index += result
                        docs_count += 1

            err_log.flush()

        #  Run test query against Milvus and log results
        if CONFIG.get("debug", True):
            logger.info("Processed documents count: %d", docs_count)
            if docs_count > 0:
                search_main()

    finally:
        connections.disconnect(alias=CONFIG["milvus"]["alias"])
        # logger.info("Disconnected from Milvus.")
