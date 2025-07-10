import tempfile
import traceback

from pathlib import Path
from typing import Optional, Tuple, Iterator
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader, CSVLoader, PDFPlumberLoader,
    UnstructuredWordDocumentLoader, UnstructuredHTMLLoader,
)
from ..utils.encoding import detect_encoding
from ..utils.hash import compute_file_hash
from readservice.utils.logger import get_logger

logger = get_logger()

FILE_LOADERS = {
    ".txt": TextLoader,
    ".csv": CSVLoader,
    ".pdf": PDFPlumberLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".doc": UnstructuredWordDocumentLoader,
    ".html": UnstructuredHTMLLoader,
}

def load_document(file_id: str, content: Optional[bytes]) -> Tuple[Iterator[Document], Optional[str], Optional[str]]:
    ext = Path(file_id).suffix.lower()
    loader_cls = FILE_LOADERS.get(ext)
    if not loader_cls:
        return iter([]), f"Unsupported file type: {file_id}", None

    # source_hash = compute_file_hash(content) if content else None
    source_hash = None

    try:
        if content:
            source_hash = compute_file_hash(content) if content else None
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                tmp.write(content)
                tmp.flush()
                file_path = tmp.name
        else:
            file_path = file_id

        if ext in [".txt", ".csv"]:
            if content:
                encoding = detect_encoding(content)
            else:
                with open(file_path, "rb") as f:
                    source_hash = compute_file_hash(f.read())
                    encoding = detect_encoding(f.read())
            if ext == ".txt":
                loader = TextLoader(file_path, encoding=encoding)
            else:  # ".csv"
                loader = CSVLoader(file_path, encoding=encoding)
        else:
            with open(file_path, "rb") as f:
                source_hash = compute_file_hash(f.read())            
            loader = loader_cls(file_path)

        if hasattr(loader, "lazy_load"):
            docs = loader.lazy_load()
        else:
            docs = iter(loader.load())

        def _inject_metadata(docs_iter):
            for doc in docs_iter:
                doc.metadata["source_hash"] = source_hash
                yield doc
 
        return _inject_metadata(docs), None, source_hash
        # return docs, None, source_hash
    except Exception as e:
        error_message = f"Error processing {file_id}: {e}"
        traceback_str = traceback.format_exc()
        logger.error(error_message)
        logger.debug(traceback_str)       

        return iter([]), error_message, None
