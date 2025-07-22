from ..utils.logger import get_logger
from .base import VectorStoreBase
import os

logger = get_logger()

def search_main(store: VectorStoreBase, CONFIG: dict) -> None:
    query = CONFIG["search"]["search_query"]

    results = store.similarity_search_with_score(query, k=CONFIG["search"]["search_top_k"])

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