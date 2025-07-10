from typing import Iterable, Iterator
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List
from readservice.utils.logger import get_logger

logger = get_logger()

def split_documents(docs: List[Document], config: dict) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
        separators=config.get("separators", None)
    )
    return splitter.split_documents(docs)

def split_documents_lazy(docs: Iterable[Document], config: dict) -> Iterator[Document]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.get("chunk_size", 1000),
        chunk_overlap=config.get("chunk_overlap", 200),
        separators=config.get("separators")
    )
    for doc in splitter.split_documents(docs):
        yield doc  # convert to a generator lazily
