import logging
import traceback
import psycopg2
from typing import List, Optional, Tuple
from langchain_core.documents import Document
from langchain_postgres import PGVector
from .base import VectorStoreBase
from ..utils.logger import get_logger

logger = get_logger()

class PGVectorStore(VectorStoreBase):
    def __init__(self, cfg: dict, embedding_function):
        self.cfg = cfg["pgvector"]
        self.pg_config = {
            "host": cfg["pgvector"]["host"],
            "port": cfg["pgvector"].get("port", 5432),
            "user": cfg["pgvector"]["user"],
            "password": cfg["pgvector"]["password"],
            "dbname": cfg["pgvector"]["database"],
        }

        # Build the connection string dynamically
        logger.info(f"Using PGVector at {cfg["pgvector"]['host']}:{cfg["pgvector"]['port']}")
        connection_string = (
            f"postgresql+psycopg2://{cfg["pgvector"]['user']}:{cfg["pgvector"]['password']}"
            f"@{cfg["pgvector"]['host']}:{cfg["pgvector"].get('port', 5432)}/{cfg["pgvector"]['database']}"
        )

        self.vstore = PGVector(
            collection_name=cfg["pgvector"]["collection"],
            connection=connection_string,
            embeddings=embedding_function,
            use_jsonb=cfg["pgvector"]["use_jsonb"],
        )

    def add_documents(self, docs: List[Document]) -> Optional[str]:
        try:
            self.vstore.add_documents(documents=docs)
            return None
        except Exception as e:
            error_message = f"[PGVECTOR ADD ERROR]: {e}"
            logger.error(error_message)
            logger.debug(traceback.format_exc())
            return str(error_message)

    def delete_by_hash(self, hashcode: str) -> Optional[str]:
        logger.info(f"Deleting documents from collection {self.cfg['collection']} with hashcode: {hashcode}")
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(**self.pg_config)
            cur = conn.cursor()
            cur.execute("""
                DELETE FROM langchain_pg_embedding
                WHERE cmetadata->>'hashcode' = %s
            """, (hashcode,))
            conn.commit()
            logger.info(f"Deleted {cur.rowcount} records with hashcode: {hashcode}")
            return None
        except Exception as e:
            error_message = f"[PGVECTOR DELETE ERROR]: {e}"
            logger.error(error_message)
            logger.debug(traceback.format_exc())
            return str(error_message)
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def get_filenames_and_hashcodes_by_source(self, source: str) -> Tuple[List[Tuple[str, str]], Optional[str]]:
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(**self.pg_config)
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT cmetadata->>'original_name', cmetadata->>'hashcode'
                FROM langchain_pg_embedding
                WHERE cmetadata->>'source' = %s
            """, (source,))
            results = cur.fetchall()
            return results, None
        except Exception as e:
            error_message = f"[PGVECTOR METADATA QUERY ERROR]: {e}"
            logger.error(error_message)
            logger.debug(traceback.format_exc())
            return [], str(error_message)            
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()


    def similarity_search_with_score(self, query: str, k: int = 4) -> List[Tuple[Document, float]]:
        logger.info(f"Performing vector search for: {query}")
        try:
            results = self.vstore.similarity_search_with_score(query, k)
            return results
        except Exception as e:
            logger.error(f"[PGVECTOR QUERY ERROR]: {e}")
            logger.debug(traceback.format_exc())
            return []   

    def document_exists(self, hashcode: str) -> Tuple[bool, Optional[str]]:
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(**self.pg_config)
            cur = conn.cursor()
            cur.execute("""
                SELECT EXISTS(
                    SELECT 1
                    FROM langchain_pg_embedding
                    WHERE cmetadata->>'hashcode' = %s
               )
            """, (hashcode,))
            return cur.fetchone()[0], None
        except Exception as e:
            error_message = f"[PGVECTOR CHECK ERROR]: {e}"
            logger.error(error_message)
            logger.debug(traceback.format_exc())            
            return False, error_message
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
