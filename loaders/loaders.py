from typing import Iterator, Optional, Tuple
from langchain_core.documents import Document
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import UnstructuredWordDocumentLoader
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain_community.document_loaders import UnstructuredExcelLoader
from ..utils.encoding import detect_encoding
import traceback
from readservice.utils.logger import get_logger
from .base_loader import BaseLoader

logger = get_logger()

class PDFPlumberLD(BaseLoader):
    def load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            loader = PDFPlumberLoader(file_path)
            return iter(loader.load()), None
        except Exception as e:
            error_message = f"Error processing {file_path} with PDFPlumberLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message

    def lazy_load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            loader = PDFPlumberLoader(file_path)
            return loader.lazy_load(), None
        except Exception as e:
            error_message = f"Error processing {file_path} with PDFPlumberLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message


class Docx2txtLD(BaseLoader):
    def load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            loader = Docx2txtLoader(file_path)
            return iter(loader.load()), None
        except Exception as e:
            error_message = f"Error processing {file_path} with Docx2txtLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message

    def lazy_load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            loader = Docx2txtLoader(file_path)
            return loader.lazy_load(), None
        except Exception as e:
            error_message = f"Error processing {file_path} with Docx2txtLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message


class  UnstructuredWordDocumentLD(BaseLoader):
    def load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            loader = UnstructuredWordDocumentLoader(file_path)
            return iter(loader.load()), None
        except Exception as e:
            error_message = f"Error processing {file_path} with UnstructuredWordDocumentLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message
        
    def lazy_load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            loader = UnstructuredWordDocumentLoader(file_path)
            return loader.lazy_load(), None
        except Exception as e:
            error_message = f"Error processing {file_path} with UnstructuredWordDocumentLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message
        
class TextLD(BaseLoader):
    def load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            # with open(file_path, "rb") as f:
            #     encoding = detect_encoding(f.read())
            # loader = TextLoader(file_path, encoding=encoding)
            loader = TextLoader(file_path, autodetect_encoding=True)
            return iter(loader.load()), None
        except Exception as e:
            error_message = f"Error processing {file_path} with TextLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message

    def lazy_load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            # with open(file_path, "rb") as f:
            #     encoding = detect_encoding(f.read())
            # loader = TextLoader(file_path, encoding=encoding)
            loader = TextLoader(file_path, autodetect_encoding=True)
            return loader.lazy_load(), None
        except Exception as e:
            error_message = f"Error processing {file_path} with TextLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message

class CSVLD(BaseLoader):
    def load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            # with open(file_path, "rb") as f:
            #     encoding = detect_encoding(f.read())
            # loader = CSVLoader(file_path, encoding=encoding)
            loader = CSVLoader(file_path, autodetect_encoding=True)
            return iter(loader.load()), None
        except Exception as e:
            error_message = f"Error processing {file_path} with CSVLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message

    def lazy_load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            # with open(file_path, "rb") as f:
            #     encoding = detect_encoding(f.read())
            # loader = CSVLoader(file_path, encoding=encoding)
            loader = CSVLoader(file_path, autodetect_encoding=True)
            return loader.lazy_load(), None
        except Exception as e:
            error_message = f"Error processing {file_path} with CSVLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message
        

class  UnstructuredHTMLLD(BaseLoader):
    def load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            loader = UnstructuredHTMLLoader(file_path)
            return iter(loader.load()), None
        except Exception as e:
            error_message = f"Error processing {file_path} with UnstructuredHTMLLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message

    def lazy_load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            loader = UnstructuredHTMLLoader(file_path)
            return loader.lazy_load(), None
        except Exception as e:
            error_message = f"Error processing {file_path} with UnstructuredHTMLLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message
        
class UnstructuredExcelLD(BaseLoader):
    def load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            loader = UnstructuredExcelLoader(file_path,mode="elements")
            return iter(loader.load()), None
        except Exception as e:
            error_message = f"Error processing {file_path} with UnstructuredExcelLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message

    def lazy_load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        try:
            loader = UnstructuredExcelLoader(file_path,mode="elements")
            return loader.lazy_load(), None
        except Exception as e:
            error_message = f"Error processing {file_path} with UnstructuredExcelLoader: {e}"
            traceback_str = traceback.format_exc()
            logger.error(error_message)
            logger.debug(traceback_str)       
            return iter([]), error_message