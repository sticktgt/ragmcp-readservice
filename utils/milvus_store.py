from langchain_milvus import Milvus
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings  # base class type
from typing import List, Optional
from pymilvus import connections, CollectionSchema, FieldSchema, DataType, Collection, utility
from ..utils.logger import get_logger
import traceback

logger = get_logger()


class MilvusStore:

    def __init__(self, cfg: dict, embedding_function: Embeddings):
        try:
            self.cfg = cfg
            connections.connect(alias=cfg["alias"], host=cfg["host"], port=cfg["port"])
            logger.info(f"Connected to Milvus at {cfg['host']}:{cfg['port']}")
            # self.ensure_milvus_collection()  # <-- Ensures schema exists before using it
            self.vstore = Milvus(
                collection_name=cfg["collection"],
                connection_args={"host": cfg["host"], "port": cfg["port"]},
                embedding_function=embedding_function,
                drop_old=cfg["drop_old"],
                auto_id=cfg["auto_id"],
            )
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
            logger.info(f"Deleting documents from collection {self.cfg['collection']} with hashcode: {hashcode}")

            if not utility.has_collection(self.cfg["collection"]):
                logger.error(f"Collection {self.cfg['collection']} does not exist.")
                return f"Collection {self.cfg['collection']} does not exist."

            collection = Collection(self.cfg["collection"])
            collection.load()
            delete_result = collection.delete(expr=f"hashcode == '{hashcode}'")

            logger.info(f"Delete result: {delete_result}")
            return None
        except Exception as e:
            logger.error(f"[MILVUS DELETE ERROR]: {e}")
            logger.debug(traceback.format_exc())
            return str(e)


    def delete_by_source(self, source: str) -> Optional[str]:
        try:
            logger.info(f"Deleting documents from collection {self.cfg['collection']} with source: {source}")

            if not utility.has_collection(self.cfg["collection"]):
                return f"Collection {self.cfg['collection']} does not exist."

            collection = Collection(self.cfg["collection"])
            collection.load()
            delete_result = collection.delete(expr=f"source == '{source}'")

            logger.info(f"Delete result: {delete_result}")
            return None
        except Exception as e:
            logger.error(f"[MILVUS DELETE ERROR]: {e}")
            logger.debug(traceback.format_exc())
            return str(e)

    def retrieve_vectors_by_hashcode(self, hashcode: str):
        connections.connect(alias=self.cfg["alias"], host=self.cfg["host"], port=self.cfg["port"])
        collection = Collection(self.cfg["collection"])
        collection.load()


        # for field in collection.schema.fields:
        #     logger.info(f"Field: {field.name}, Type: {field.dtype}, Is Primary: {field.is_primary}")

        expr = f"hashcode == '{hashcode}'"
        output_fields = ["vector"]
        results = collection.query(expr=expr, output_fields=output_fields)

        vectors = [r["vector"] for r in results if "vector" in r]
        logger.info(f"Retrieved {len(vectors)} vectors for hashcode: {hashcode}")
        # for i, vec in enumerate(vectors):
        #    logger.info(f"Vector {i}: {vec[:5]}...")  # Print first 5 dims for debug
    
