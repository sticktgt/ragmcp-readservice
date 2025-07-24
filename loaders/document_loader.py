import tempfile
import traceback

from pathlib import Path
from typing import Optional, Tuple, Iterator
from langchain_core.documents import Document
from ..utils.encoding import detect_encoding
from ..utils.hash import compute_file_hash
from readservice.utils.logger import get_logger
from .loader_factory import get_loader


logger = get_logger()


def save_temp_file(file_id: str, content: bytes, suffix: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        file_path = tmp.name
    return file_path


def load_document(file_id: str, content: Optional[bytes], file_types_cfg: dict) -> Tuple[Iterator[Document], Optional[str], Optional[str]]:
    ext = Path(file_id).suffix.lower()

    loader = get_loader(ext, file_types_cfg)
    if not loader:
        return iter([]), f"Unsupported file type: {ext}", None

    # source_hash = None
    try:
        if content:
            source_hash = compute_file_hash(content) if content else None
            file_path = save_temp_file(file_id, content, ext)
        else:
            file_path = file_id
            with open(file_path, "rb") as f:
                source_hash = compute_file_hash(f.read())

        if hasattr(loader, "lazy_load"):
            docs, error_message = loader.lazy_load(file_path)
        else:
            docs, error_message = loader.load(file_path)
        if error_message:
            return iter([]), error_message, source_hash

        def _inject_metadata(docs_iter):
            for doc in docs_iter:
                doc.metadata["hashcode"] = source_hash
                yield doc
 
        return _inject_metadata(docs), None, source_hash
    except Exception as e:
        error_message = f"Error processing {file_id}: {e}"
        traceback_str = traceback.format_exc()
        logger.error(error_message)
        logger.debug(traceback_str)       

        return iter([]), error_message, None
