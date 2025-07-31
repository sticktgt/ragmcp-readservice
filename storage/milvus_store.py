from langchain_milvus import Milvus
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings  # base class type
from typing import List, Optional, Tuple
# from pymilvus import Collection, utility
from ..utils.logger import get_logger
import traceback
from .base import VectorStoreBase

logger = get_logger()


class MilvusStore(VectorStoreBase):

    def __init__(self, cfg: dict, embedding_function: Embeddings):
        try:
            self.cfg = cfg["milvus"]
            self.vstore = Milvus(
                collection_name=cfg["milvus"]["collection"],
                connection_args={"uri": cfg["milvus"]["uri"]},
                embedding_function=embedding_function,
                drop_old=cfg["milvus"]["drop_old"],
                auto_id=cfg["milvus"]["auto_id"],
            )
            logger.info(f"Using Milvus at {cfg["milvus"]['uri']}")
        except Exception as e:
            logger.error(f"[MILVUS INIT ERROR]: {e}")
            logger.debug(traceback.format_exc())
            raise

    def add_documents(self, docs: List[Document]) -> Optional[str]:
        try:
            self.vstore.add_documents(documents=docs)
            return None
        except Exception as e:
            logger.error(f"[MILVUS ADD ERROR]: {e}")
            logger.debug(traceback.format_exc())
            return str(e)

    def document_exists(self, hashcode: str) -> Tuple[bool, Optional[str]]:
        try:
            results = self.vstore.search_by_metadata(
                expr=f"hashcode == '{hashcode}'",
                limit=1
            )
            return bool(results), None
        except Exception as e:
            error_message = f"[MILVUS CHECK ERROR]: {e}"
            logger.warning(error_message)
            logger.debug(traceback.format_exc())
            return False, error_message

    def get_filenames_and_hashcodes_by_source(self, source: str) -> Tuple[List[Tuple[str, str]], Optional[str]]:
        """
        Returns a list of (original_name, hashcode) tuples for a given source directory.
        """
        try:
            results = self.vstore.search_by_metadata(
                expr=f"source == '{source}'",
                fields=["original_name", "hashcode", "text"],  # include "text" to fetch records
                limit=10000
            )
            seen = set()
            unique_pairs = []
            for doc in results:
                name = doc.metadata.get("original_name")
                hashcode = doc.metadata.get("hashcode")
                if name and hashcode:
                    key = name.lower()  # Case-insensitive check
                    if key not in seen:
                        seen.add(key)
                        unique_pairs.append((name, hashcode))
            return unique_pairs, None
        except Exception as e:
            error_message = f"[MILVUS HASHCODE QUERY ERROR]: {e}"
            logger.error(error_message)
            logger.debug(traceback.format_exc())
            return [], error_message

        
    def delete_by_hash(self, hashcode: str) -> Optional[str]:
        try:
            logger.info(f"Deleting documents from collection {self.cfg['collection']} with hashcode: {hashcode}")
            delete_result = self.vstore.delete(None,expr=f"hashcode == '{hashcode}'")

            logger.info(f"Delete result: {delete_result}")
            return None
        except Exception as e:
            logger.error(f"[MILVUS DELETE ERROR]: {e}")
            logger.debug(traceback.format_exc())
            return str(e)

    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        try:
            logger.info(f"Performing vector search for: {query}")
            results = self.vstore.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            logger.error(f"[MILVUS QUERY ERROR]: {e}")
            logger.debug(traceback.format_exc())
            return []        