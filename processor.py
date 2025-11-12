import os
from pathlib import Path
from typing import Any, Optional, Tuple
import multiprocessing as mp

from .output.saver import save_doc_text, save_metadata_entry
from .loaders.document_loader import load_document
from .sources.local import LocalFileSource
from .sources.s3 import S3FileSource
# from .config import CONFIG
from .config import get_config
from .utils.logger import get_logger
from .embedding.embedding import get_embedding_function
from .storage.base import VectorStoreBase
from .storage.factory import get_vector_store
from .storage.search import search_main
from .splitters.document_splitter import split_documents_lazy

import traceback

logger = get_logger()

# -------- Timeout helpers --------
def _subproc_entry(q, config: dict, file_id: str, content: Optional[bytes], meta: dict,
                   doc_index: int, output_dir: str, meta_path: str, error_path: str):
    """
    Child process entry: recreate embedding+store here (avoid pickling live clients),
    then run the normal handle_file() and send the integer result back.
    """
    try:
        embedding_function = get_embedding_function(config["embedding"])
        store = get_vector_store(config["storage"], embedding_function)
        # open error log in append mode inside child
        with open(error_path, "a", encoding="utf-8") as err_log:
            res = handle_file(file_id, content, meta, store, doc_index, err_log, output_dir, meta_path, config)
        q.put(("ok", res))
    except Exception as e:
        q.put(("err", f"{e}"))

def run_with_timeout(seconds: int, *args, **kwargs) -> int:
    """
    Run _subproc_entry in a spawned process and enforce a hard timeout.
    Returns the int result from handle_file or raises TimeoutError/RuntimeError.
    """
    # ctx = mp.get_context("spawn")
    # Prefer fork on Linux (no re-import), fall back to spawn elsewhere
    try:
        ctx = mp.get_context("fork")
    except ValueError:
        ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_subproc_entry, args=(q,)+args, kwargs=kwargs)
    p.start()
    p.join(seconds)
    if p.is_alive():
        p.terminate()
        p.join(5)
        raise TimeoutError("Per-file timeout exceeded")
    #status, payload = q.get()
    # Child finished. If it crashed before writing to the queue, avoid blocking here.
    if q.empty():
        raise RuntimeError("Child process exited without returning a result")
    status, payload = q.get()

    if status == "ok":
        return payload
    raise RuntimeError(payload)

def is_already_uploaded(hashcode: str, store: VectorStoreBase) -> Tuple[bool, Optional[str]]:
    return store.document_exists(hashcode)


def handle_file(file_id: str, content: Optional[bytes], meta: dict,
                store: VectorStoreBase, doc_index: int,
                err_log, output_dir: str, meta_path: str, config: dict) -> int:
    """Handle a single file: load, split, embed, and store."""
    file_parts = 0
    try:
        logger.info(f"Processing: {file_id}")
        docs, load_error, source_hash = load_document(file_id, content, config["file_types"])
        if load_error:
            logger.error(f"[LOAD ERROR] {file_id}: {load_error}")
            err_log.write(f"[LOAD ERROR] {file_id}: {load_error}\n")
            return 0

        # if CONFIG.get("debug", True):
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
                if config.get("delete_old_vectors", False): # for a test purpose only!!
                    store.delete_by_hash(source_hash) # for a test purpose only!!
                return 0
            source = meta.get("source")
            original_name = meta.get("original_name", "").lower()
            if source and original_name:
                # Search for existing documents by the same source
                edocs, edocs_error = store.get_filenames_and_hashcodes_by_source(source)
                if edocs_error:
                    logger.error(f"[SEARCH ERROR] {file_id}: {edocs_error}")
                    err_log.write(f"[SEARCH ERROR] {file_id}: {edocs_error}\n")
                    return 0
                logger.debug(f"[SEARCH] found {len(edocs)} existing documents with source: {source}")
                if config.get("debug", False):
                    if len(edocs) > 0:
                        logger.debug(f"[SEARCH] {edocs}")
                for existing_name, existing_hash in edocs:
                    if existing_name.lower() == original_name:
                        logger.info(f"[DUPLICATE] Found matching file in Milvus: {existing_name} (hash: {existing_hash})")
                        store.delete_by_hash(existing_hash)

        ext = Path(file_id).suffix.lower()
        split_docs, split_error = split_documents_lazy(docs, file_ext=ext, config=config)
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

        for doc in chunk_docs:
            if config.get("debug", True):
                save_doc_text(doc, doc_index, output_dir)
                save_metadata_entry(doc, doc_index, meta_path)
            doc_index += 1

        logger.info(f"Processed {file_id}: {file_parts} parts, {len(chunk_docs)} chunks")

        return len(chunk_docs)

    except Exception as e:
        logger.error(f"[CRITICAL ERROR] {file_id}: {e}")
        err_log.write(f"[CRITICAL ERROR] {file_id}: {e}\n")
        logger.debug(traceback.format_exc())
        return -1

def process_streaming() -> bool:
    CONFIG = get_config()
    doc_index = 0
    docs_count = 0
    store = None
    had_fatal_error = False
    try:
        output_dir = CONFIG["output_dir"]
        os.makedirs(output_dir, exist_ok=True)
        meta_path = os.path.join(output_dir, "metadata.jsonl")
        error_path = os.path.join(output_dir, "errors.log")

        embedding_function = get_embedding_function(CONFIG["embedding"])
        #store = MilvusStore(CONFIG["milvus"], embedding_function=embedding_function)
        store = get_vector_store(CONFIG["storage"], embedding_function)
        # Per-file timeout (seconds), configurable but safe default:
        per_file_seconds = int(CONFIG.get("timeouts", {}).get("perFileSeconds", 90))

        sources = []
        if CONFIG["sources"].get("use_local"):
            sources.append(LocalFileSource(CONFIG["sources"]["local_path"], CONFIG["file_types"]))
        if CONFIG["sources"].get("use_s3"):
            sources.append(S3FileSource(CONFIG["sources"], CONFIG["file_types"]))

        with open(error_path, "w", encoding="utf-8") as err_log:
            for source in sources:
                logger.info(f"Processing source: {source.__class__.__name__}")
                for file_id, content, meta, source_error in source.iterate_files():
                    if source_error:
                        logger.error(f"[SOURCE ERROR] {file_id}: {source_error}")
                        err_log.write(f"[SOURCE ERROR] {file_id}: {source_error}\n")
                        continue

                    # result = handle_file(file_id, content, meta, store, doc_index, err_log, output_dir, meta_path)
                    try:
                        # Run the whole file in an isolated child and enforce a hard timeout
                        result = run_with_timeout(
                            per_file_seconds,
                            CONFIG, file_id, content, meta, doc_index, output_dir, meta_path, error_path
                       )
                    except TimeoutError:
                        logger.error(f"[TIMEOUT] {file_id} exceeded {per_file_seconds}s — skipping")
                        err_log.write(f"[TIMEOUT] {file_id} exceeded {per_file_seconds}s\n")
                        continue
                    except Exception as e:
                        logger.critical(f"[FATAL] Subprocess error in file {file_id}: {e}")
                        had_fatal_error = True
                        break

                    if result < 0:
                        logger.critical(f"[FATAL] Aborting due to error in file: {file_id}")
                        had_fatal_error = True
                        break
                        # return
                    elif result > 0:
                        doc_index += result
                        docs_count += 1
                if had_fatal_error:
                    break
            err_log.flush()

        logger.info("Processed documents count: %d", docs_count)
        #  Run test query and log results
        if CONFIG.get("debug", True):
            if docs_count > 0:
                # Recreate a store just for the debug search (avoid reusing child connections)
                ef = get_embedding_function(CONFIG["embedding"])
                store_for_search = get_vector_store(CONFIG["storage"], ef)
                search_main(store_for_search, CONFIG)               
                # search_main(store, CONFIG)

    finally:
        logger.debug("")
        return not had_fatal_error
