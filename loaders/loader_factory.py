from typing import Optional, Type
from .loaders import PDFPlumberLD
from .loaders import Docx2txtLD
from .loaders import UnstructuredWordDocumentLD
from .loaders import TextLD
from .loaders import CSVLD
from .loaders import UnstructuredHTMLLD
from .loaders import UnstructuredExcelLD
from .loaders import PyMuPDFLD
from .loaders import BSHTMLLD
from .loaders import UnstructuredPowerPointLD
from .base_loader import BaseLoader
from readservice.utils.logger import get_logger

logger = get_logger()

LOADER_MAPPING: dict[str, Type[BaseLoader]] = {
    "PDFPlumberLoader": PDFPlumberLD,
    "Docx2txtLoader": Docx2txtLD,
    "UnstructuredWordDocumentLoader": UnstructuredWordDocumentLD,
    "PDFPlumberLoader": TextLD,
    "TextLoader": CSVLD,
    "UnstructuredHTMLLoader": UnstructuredHTMLLD,
    "UnstructuredExcelLoader": UnstructuredExcelLD,
    "PyMuPDFLoader": PyMuPDFLD,
    "BSHTMLLoader": BSHTMLLD,
    "UnstructuredPowerPointLoader": UnstructuredPowerPointLD
}


def get_loader(file_ext: str, file_types_config: dict) -> Optional[BaseLoader]:
    file_config = file_types_config.get(file_ext)
    if not file_config:
        return None

    loader_name = file_config.get("loader")
    loader_class = LOADER_MAPPING.get(loader_name)

    if loader_class:
        return loader_class(file_config)
    return None
