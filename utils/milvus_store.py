import traceback
from typing import List, Optional

from langchain_community.vectorstores import Milvus
from langchain_core.documents import Document
from pymilvus import connections
from langchain_core.embeddings import Embeddings
import uuid
from readservice.utils.logger import get_logger

logger = get_logger()


class DummyEmbeddings(Embeddings):
    def __init__(self, dim: int):
        self.dim = dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] * self.dim for _ in texts]

    def embed_query(self, text: str) -> List[float]:
        return [0.0] * self.dim


class MilvusStore:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        try:
            connections.connect(alias="default", host=cfg["host"], port=cfg["port"])
            logger.info(f"Connected to Milvus at {cfg['host']}:{cfg['port']}")

            self.vstore = Milvus(
                embedding_function=DummyEmbeddings(cfg["dim"]),
                collection_name=cfg["collection"],
                connection_args={"host": cfg["host"], "port": cfg["port"]}
            )
        except Exception as e:
            logger.error(f"[MILVUS INIT ERROR]: {e}")
            logger.debug(traceback.format_exc())
            raise

    def add_documents(self, docs: List[Document], embeddings: List[List[float]]) -> Optional[str]:
        try:
            texts = [doc.page_content for doc in docs]
            metadatas = [doc.metadata for doc in docs]
            # Generate unique ids from source hash or fallback
            ids = [str(uuid.uuid4()) for doc in docs]
            self.vstore.add_texts(
                texts=texts,
                metadatas=metadatas,
                embeddings=embeddings,
                ids=ids
            )
            return None
        except Exception as e:
            logger.error(f"[MILVUS ADD ERROR]: {e}")
            logger.debug(traceback.format_exc())
            return str(e)

    def document_exists(self, hashcode: str) -> bool:
        try:
            results = self.vstore.similarity_search_with_score(query=hashcode, k=1)
            return bool(results)
        except Exception as e:
            logger.warning(f"[MILVUS CHECK ERROR]: {e}")
            return False

    def query_by_source(self, source: str):
        try:
            return self.vstore.similarity_search(query=source, k=5)
        except Exception as e:
            logger.error(f"[MILVUS QUERY ERROR]: {e}")
            logger.debug(traceback.format_exc())
            return []

    def query_by_hashcode(self, hashcode: str):
        try:
            return self.vstore.similarity_search(query=hashcode, k=5)
        except Exception as e:
            logger.error(f"[MILVUS QUERY ERROR]: {e}")
            logger.debug(traceback.format_exc())
            return []

    def delete_by_hash(self, hashcode: str) -> Optional[str]:
        try:
            self.vstore.delete(delete_filter=f"hashcode == '{hashcode}'")
            return None
        except Exception as e:
            logger.error(f"[MILVUS DELETE ERROR]: {e}")
            logger.debug(traceback.format_exc())
            return str(e)

    def delete_by_source(self, source: str) -> Optional[str]:
        try:
            self.vstore.delete(delete_filter=f"source == '{source}'")
            return None
        except Exception as e:
            logger.error(f"[MILVUS DELETE ERROR]: {e}")
            logger.debug(traceback.format_exc())
            return str(e)
