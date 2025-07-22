from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from langchain_core.documents import Document

class VectorStoreBase(ABC):
    @abstractmethod
    def add_documents(self, docs: List[Document]) -> Optional[str]:
        pass

    @abstractmethod
    def delete_by_hash(self, hashcode: str) -> Optional[str]:
        pass

    #def get_distinct_filenames_by_source(self, source: str) -> Tuple[List[str], Optional[str]]:
    @abstractmethod
    def get_filenames_and_hashcodes_by_source(self, source: str) -> Tuple[List[Tuple[str, str]], Optional[str]]:
        pass

    @abstractmethod
    def document_exists(self, hashcode: str) -> Tuple[bool, Optional[str]]:
        pass

    @abstractmethod
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        pass