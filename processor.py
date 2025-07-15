import os
from pathlib import Path
from .output.saver import save_doc_text, save_metadata_entry
from .loaders.document_loader import load_document
from .sources.local import LocalFileSource
from .sources.s3 import S3FileSource
from .config import CONFIG
from .utils.splitters import split_documents_lazy
from .utils.embedding import embed_documents
from .utils.logger import get_logger
import traceback
from .utils.milvus_store import MilvusStore

from itertools import tee

logger = get_logger()

def is_already_uploaded(hashcode: str, store: MilvusStore) -> bool:
    return store.document_exists(hashcode)

def process_streaming():
    output_dir = CONFIG["output_dir"]
    meta_path = os.path.join(output_dir, "metadata.jsonl")
    error_path = os.path.join(output_dir, "errors.log")
    os.makedirs(output_dir, exist_ok=True)

    doc_index = 0

    sources = []
    if CONFIG.get("use_local"):
        sources.append(LocalFileSource(CONFIG["local_path"], CONFIG["file_types"]))
    if CONFIG.get("use_s3"):
        sources.append(S3FileSource(CONFIG, CONFIG["file_types"]))

    # Optional debug counters
    counters = {
        "files": 0,
        "documents": 0,
        "chunks": 0,
    }
    debug = CONFIG.get("debug_counters", False)
    store = MilvusStore(CONFIG["milvus"])

    with open(error_path, "w", encoding="utf-8") as err_log:
        for source in sources:
            try:
                logger.info(f"Processing source: {source.__class__.__name__}")
                for file_id, content, meta, source_error in source.iterate_files():
                    if debug:
                        counters["documents"] = 0
                        counters["chunks"] = 0
                        counters["files"] += 1                    
                    logger.info(f"Processing: {file_id}")

                    if source_error:
                        logger.error(f"[SOURCE ERROR] {file_id}: {source_error}")
                        err_log.write(f"[SOURCE ERROR] {file_id}: {source_error}\n")
                        continue

                    docs, load_error, source_hash = load_document(file_id, content)
                    if load_error:
                        logger.error(f"[LOAD ERROR] {file_id}: {load_error}")
                        err_log.write(f"[LOAD ERROR] {file_id}: {load_error}\n")
                        continue

                    if debug:
                        docs, docs_copy = tee(docs)
                        counters["documents"] += sum(1 for _ in docs_copy)

                    if source_hash and is_already_uploaded(source_hash, store):
                        logger.info(f"Skipping {file_id}, Hashcode {source_hash}: already exists in Milvus.")
                        continue

                    ext = Path(file_id).suffix.lower()

                    split_docs, split_error = split_documents_lazy(docs, file_ext=ext, config=CONFIG["splitters"])
                    if split_error:
                        logger.error(f"[SPLIT ERROR] {file_id}: {split_error}")
                        err_log.write(f"[SPLIT ERROR] {file_id}: {split_error}\n")
                        continue

                    for split_doc in split_docs:
                        split_doc.metadata.update(meta)                

                        if debug:
                            counters["chunks"] += 1

                        embedded, embed_error = embed_documents(split_doc)
                        if embed_error:
                            logger.error(f"[EMBED ERROR] {file_id}: {embed_error}")
                            err_log.write(f"[EMBED ERROR] {file_id}: {embed_error}\n")
                            continue
                        if debug:
                            logger.info(f"Embedded contents: {embedded}")

                        # Milvus insert
                        add_error = store.add_documents([split_doc], embedded[0]["embedding"])
                        if add_error:
                            logger.error(f"[MILVUS ERROR] {file_id}: {add_error}")
                            err_log.write(f"[MILVUS ERROR] {file_id}: {add_error}\n")
                            continue
                            
                        if debug:
                            save_doc_text(split_doc, doc_index, output_dir)
                        save_metadata_entry(split_doc, doc_index, meta_path)
                        doc_index += 1   
                    if debug:
                        logger.info(f"[SUMMARY] Documents loaded: {counters['documents']}")
                        logger.info(f"[SUMMARY] Chunks created: {counters['chunks']}")
                        # Optional debug verification
                    if debug and source_hash:
                        result = store.query_by_hashcode(source_hash)
                        logger.info(f"Milvus query returned {len(result)} vectors for hash {source_hash}")                        
   
            except Exception as e:
                error_message = f"[PROCESSING ERROR] {source.__class__.__name__}: {e}"
                traceback_str = traceback.format_exc()
                logger.debug(traceback_str)                      
                logger.error(e)
                err_log.write(error_message + "\n")
