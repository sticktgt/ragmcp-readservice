from langchain_milvus import Milvus
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings  # base class type
from typing import List, Optional, Tuple
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

    def query_by_source(self, source: str) -> Tuple[List[Document], Optional[str]]:
        try:
            return self.vstore.search_by_metadata(
                # expr = f"source == '{source}' and original_name == '{filename}'"
                expr=f"source == '{source}'",
                fields=["source", "original_name", "text"], # should include "text"!!!
                limit=10000
            ), None
        except Exception as e:
            error_message = f"[MILVUS QUERY ERROR]: {e}"
            logger.error(error_message)
            logger.debug(traceback.format_exc())
            return [], error_message

    def get_distinct_filenames_by_source(self, source: str) -> Tuple[List[str], Optional[str]]:
        try:
            results = self.vstore.search_by_metadata(
                expr=f"source == '{source}'",
                fields=["original_name", "text"], # should include "text"!!!
                limit=10000
            )
            # Extract distinct original_names
            unique_names = list({
                name for doc in results 
                    if (name := doc.metadata.get("original_name")) is not None
            })
            return unique_names, None
        except Exception as e:
            error_message = f"[MILVUS DISTINCT QUERY ERROR]: {e}"
            logger.error(error_message)
            logger.debug(traceback.format_exc())
            return [], error_message


    def query_by_hashcode(self, hashcode: str):
        try:
            return self.vstore.search_by_metadata(
                expr=f"hashcode == '{hashcode}'",
                limit=10
            )
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

    # Just for debugging purposes
    def retrieve_vectors_by_hashcode(self, hashcode: str):
        connections.connect(alias=self.cfg["alias"], host=self.cfg["host"], port=self.cfg["port"])
        collection = Collection(self.cfg["collection"])
        collection.load()
        # to see the collection schema
        # for field in collection.schema.fields:
        #     logger.info(f"Field: {field.name}, Type: {field.dtype}, Is Primary: {field.is_primary}")

        expr = f"hashcode == '{hashcode}'"
        output_fields = ["vector"]
        results = collection.query(expr=expr, output_fields=output_fields)

        vectors = [r["vector"] for r in results if "vector" in r]
        logger.info(f"Retrieved {len(vectors)} vectors for hashcode: {hashcode}")
        # to see the first few vectors
        # for i, vec in enumerate(vectors):
        #     logger.info(f"Vector {i}: {vec[:5]}...")  # Print first 5 dims for debug
    
    # Just for debugging purposes
    def print_by_hashcode(self, hashcode: str):
        try:
            result = self.vstore.search_by_metadata(
                expr=f"hashcode == '{hashcode}'",
                limit=100
            )
            if result:
                logger.info(f"Found {len(result)} documents with hashcode: {hashcode}")
                logger.info(f"{result}")
            else:
                logger.info(f"No documents found with hashcode: {hashcode}")
        except Exception as e:
            logger.error(f"[MILVUS QUERY ERROR]: {e}")
            logger.debug(traceback.format_exc())
            return []

