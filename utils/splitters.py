
from typing import Iterable, Iterator, Tuple, Optional
from langchain_core.documents import Document
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
    NLTKTextSplitter,
)
from readservice.utils.logger import get_logger
import traceback

logger = get_logger()

def get_splitter(splitter_type: str, chunk_size: int, chunk_overlap: int, **kwargs):
    if splitter_type == "recursive":
        return RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs)
    elif splitter_type == "token":
        return TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    elif splitter_type == "nltk":
        return NLTKTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    else:
        raise ValueError(f"Unsupported splitter type: {splitter_type}")

def split_documents_lazy(docs: Iterable[Document], file_ext: str, config: dict) -> Tuple[Iterator[Document], Optional[str]]:    
    try:
        file_config = config.get(file_ext, {})
        splitter_type = file_config.get("type", "recursive")

        if splitter_type == "none":
           return iter(docs), None

        chunk_size = file_config.get("chunk_size", 1000)
        chunk_overlap = file_config.get("chunk_overlap", 50)
        extra_args = {k: v for k, v in file_config.items() if k not in ["type", "chunk_size", "chunk_overlap"]}

        splitter = get_splitter(splitter_type, chunk_size=chunk_size, chunk_overlap=chunk_overlap, **extra_args)
        return iter(splitter.split_documents(docs)), None
    except Exception as e:
        error_message = f"Splitter error for type {file_ext}: {e}"
        logger.error(e)
        logger.debug(traceback.format_exc())
        return iter([]), error_message