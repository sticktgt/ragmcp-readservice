from abc import ABC, abstractmethod
from typing import Iterator, Optional, Tuple
from langchain_core.documents import Document

class BaseLoader(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        pass

    @abstractmethod
    def lazy_load(self, file_path: str) -> Tuple[Iterator[Document], Optional[str]]:
        pass