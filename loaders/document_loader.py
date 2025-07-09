import tempfile
import traceback

from pathlib import Path
from typing import Optional, Tuple, List
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader, CSVLoader, PDFPlumberLoader,
    UnstructuredWordDocumentLoader, UnstructuredHTMLLoader,
)
from ..utils.encoding import detect_encoding
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

def load_document(file_id: str, content: Optional[bytes]) -> Tuple[List[Document], Optional[str]]:
    ext = Path(file_id).suffix.lower()
    loader_cls = FILE_LOADERS.get(ext)
    if not loader_cls:
        return [], f"Unsupported file type: {file_id}"

    try:
        if content:
            with tempfile.NamedTemporaryFile(suffix=ext) as tmp:
                tmp.write(content)
                tmp.flush()
                file_path = tmp.name
                if ext == ".txt":
                    encoding = detect_encoding(content)
                    loader = TextLoader(file_path, encoding=encoding)
                else:
                    loader = loader_cls(file_path)
                docs = loader.load()
        else:
            file_path = file_id
            if ext == ".txt":
                with open(file_path, "rb") as f:
                    encoding = detect_encoding(f.read())
                loader = TextLoader(file_path, encoding=encoding)
            else:
                loader = loader_cls(file_path)
            docs = loader.load()

        return docs, None
    except Exception as e:
        error_message = f"Error processing {file_id}: {e}"
        traceback_str = traceback.format_exc()
        logger.error(error_message)
        logger.debug(traceback_str)       

        return [], error_message
