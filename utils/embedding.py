
from typing import List, Tuple, Optional, Union
from langchain_core.documents import Document
from readservice.config import CONFIG
from readservice.utils.logger import get_logger
import traceback
# from langchain.embeddings import OpenAIEmbeddings

logger = get_logger()

def embed_documents(docs: Union[Document, List[Document]]) -> Tuple[List[dict], Optional[str]]:
    if isinstance(docs, Document):
        docs = [docs]    
    try:
        """Simulate embedding by returning dummy vectors with metadata."""
        fake_vector = [round(0.01 * i, 5) for i in range(1, 6)]  # e.g., [0.01, 0.02, ...]
        embedded = []

        for doc in docs:
            embedded.append({
                "embedding": fake_vector,
                "metadata": doc.metadata
            })
        return embedded, None

        # embedder = OpenAIEmbeddings(
        #     openai_api_base=CONFIG["embedding"]["endpoint"],
        #     openai_api_key=CONFIG["embedding"]["api_key"],
        #     model=CONFIG["embedding"]["model"]
        # )
        # vectors = embedder.embed_documents([doc.page_content for doc in docs])

    except Exception as e:
        error_message = f"Embedding error: {e}"
        logger.error(error_message)
        logger.debug(traceback.format_exc())
        return [], error_message