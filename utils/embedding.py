
from typing import List, Tuple, Optional, Union
from langchain_core.documents import Document
from readservice.config import CONFIG
from readservice.utils.logger import get_logger
import traceback
# from langchain.embeddings import OpenAIEmbeddings

logger = get_logger()

# Optional: import real YandexGPT embedder if enabled
try:
    from langchain_community.embeddings.yandex import YandexGPTEmbeddings
except ImportError:
    YandexGPTEmbeddings = None

def embed_documents(docs: Union[Document, List[Document]]) -> Tuple[List[dict], Optional[str]]:
    if isinstance(docs, Document):
        docs = [docs]    

    provider = CONFIG.get("embedding", {}).get("provider", "fake")

    try:

        if provider == "yandex":
            if not YandexGPTEmbeddings:
                raise ImportError("YandexGPTEmbeddings not available. Please install langchain-community")

            api_key = CONFIG["yandex"]["api_key"]
            folder_id = CONFIG["yandex"]["folder_id"]
            embedder = YandexGPTEmbeddings(
                api_key=api_key,
                folder_id=folder_id,
                grpc_metadata=[],
                disable_request_logging=False,
                sleep_interval=2.0,
                doc_model_name="text-search-doc",   # Embedding for your document chunks
                model_version="latest",
            )
            vectors = embedder.embed_documents([doc.page_content for doc in docs])
        else:
            # fallback to dummy vector
            logger.debug("Using fake embedding provider for simulation.")
            vectors = [[round(0.01 * i, 5) for i in range(1, 6)]] * len(docs)  # e.g., [0.01, 0.02, ...]

        embedded = []
        for doc, vector in zip(docs, vectors):
            embedded.append({
                "embedding": vector,
                "metadata": doc.metadata
            })

        # embedder = OpenAIEmbeddings(
        #     openai_api_base=CONFIG["embedding"]["endpoint"],
        #     openai_api_key=CONFIG["embedding"]["api_key"],
        #     model=CONFIG["embedding"]["model"]
        # )
        # vectors = embedder.embed_documents([doc.page_content for doc in docs])

        return embedded, None

    except Exception as e:
        error_message = f"Embedding error: {e}"
        logger.error(error_message)
        logger.debug(traceback.format_exc())
        return [], error_message