from readservice.utils.embedding import get_embedding_function
from readservice.utils.logger import get_logger
from readservice.config import CONFIG
from langchain_core.documents import Document
from langchain_milvus import Milvus
from pymilvus import connections
import os

logger = get_logger()

def search_milvus(query: str, k: int = 5) -> list:
    # Initialize embedding
    embedding_fn = get_embedding_function(CONFIG["embedding"])
    # query_vector = embedding_fn.embed_query(query)

    # Connect Milvus and create store
    milvus_cfg = CONFIG["milvus"]
    connections.connect(alias=milvus_cfg["alias"], host=milvus_cfg["host"], port=milvus_cfg["port"])

    store = Milvus(
        collection_name=milvus_cfg["collection"],
        connection_args={"host": milvus_cfg["host"], "port": milvus_cfg["port"]},
        embedding_function=embedding_fn,
        drop_old=False,
        auto_id=milvus_cfg["auto_id"],
    )

    logger.info(f"Performing vector search for: {query}")
    results = store.similarity_search_with_score(query, k=k)
    return results

def search_main(): #CONFIG["yandex"]["api_key"]
    query = CONFIG["milvus"]["search_query"]
    k = CONFIG["milvus"]["search_top_k"]

    results = search_milvus(query, k)

    output_file = os.path.join(CONFIG["output_dir"], "search_results.txt")
    with open(output_file, "w", encoding="utf-8") as f:
        if not results:
            msg = "No matches found."
            logger.info(msg)
            f.write(msg + "\n")
            return

        for i, (doc, score) in enumerate(results):
            summary = doc.page_content[:200].replace("\n", " ") + "..." if len(doc.page_content) > 200 else doc.page_content
            log_entry = (
                f"[{i + 1}] Score: {score:.4f}\n"
                f"Content: {summary}\n"
                f"Metadata: {doc.metadata}\n"
            )
            # logger.info(log_entry)
            f.write(log_entry + "\n")

    logger.info(f"Search results written to: {output_file}")
