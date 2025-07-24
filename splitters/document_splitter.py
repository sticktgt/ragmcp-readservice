from .splitter_factory import get_splitter
from readservice.utils.logger import get_logger
from typing import Iterable, Iterator, Tuple, Optional
from langchain_core.documents import Document
import traceback

logger = get_logger()

def split_documents_lazy(docs: Iterable[Document], file_ext: str, config: dict) -> Tuple[Iterator[Document], Optional[str]]:    
    try:
        type_config = config.get(file_ext, {})
        splitter_config = type_config["splitter"]
        splitter = get_splitter(splitter_config)

        if splitter == None:
           return iter(docs), None

        return iter(splitter.split_documents(docs)), None
    except Exception as e:
        error_message = f"Splitter error for type {file_ext}: {e}"
        logger.error(e)
        logger.debug(traceback.format_exc())
        return iter([]), error_message