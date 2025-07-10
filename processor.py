import os
from .output.saver import save_doc_text, save_metadata_entry
from .loaders.document_loader import load_document
from .sources.local import LocalFileSource
from .sources.s3 import S3FileSource
from .config import CONFIG
from .utils.splitters import split_documents_lazy
from readservice.utils.logger import get_logger
import traceback

logger = get_logger()

def is_already_uploaded(hashcode: str) -> bool:
    # Stub method - replace with real Milvus filter
    return False

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

    with open(error_path, "w", encoding="utf-8") as err_log:
        for source in sources:
            logger.info(f"Processing source: {source.__class__.__name__}")
            for file_id, content, meta, source_error in source.iterate_files():
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

                if source_hash and is_already_uploaded(source_hash):
                    logger.info(f"Skipping {file_id}, Hashcode {source_hash}: already exists in Milvus.")
                    continue

                try:
                    for split_doc in split_documents_lazy(docs, CONFIG["splitter"]):
                        split_doc.metadata.update(meta)
                        save_doc_text(split_doc, doc_index, output_dir)
                        save_metadata_entry(split_doc, doc_index, meta_path)
                        doc_index += 1
                except Exception as e:
                    traceback_str = traceback.format_exc()
                    logger.debug(traceback_str)                      
                    logger.error(f"[SPLIT ERROR] {file_id}: {e}")
                    err_log.write(f"[SPLIT ERROR] {file_id}: {e}\n")
