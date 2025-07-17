
from typing import Callable, List, Tuple, Optional, Union
from langchain_core.documents import Document
from readservice.config import CONFIG
from readservice.utils.logger import get_logger
import traceback
from langchain_core.embeddings import Embeddings

logger = get_logger()

class CustomEmbeddings(Embeddings):
    def __init__(self, embedding_fn: Callable[[List[str]], List[List[float]]]):
        self._embedding_fn = embedding_fn

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embedding_fn(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._embedding_fn([text])[0]

# Optional: import real YandexGPT embedder if enabled
try:
    from langchain_community.embeddings.yandex import YandexGPTEmbeddings
except ImportError:
    YandexGPTEmbeddings = None

def get_embedding_function(cfg: dict) -> Embeddings:
    provider = cfg.get("provider", "fake")
    if provider == "yandex":
        logger.debug("Using YandexGPT embeddings provider.")
        from langchain_community.embeddings.yandex import YandexGPTEmbeddings
        return YandexGPTEmbeddings(
            api_key=CONFIG["yandex"]["api_key"],
            folder_id=CONFIG["yandex"]["folder_id"],
            doc_model_name=CONFIG["yandex"].get("doc_model_name", "text-search-doc"),
            disable_request_logging=CONFIG["yandex"].get("disable_request_logging", False),
            sleep_interval=CONFIG["yandex"].get("sleep_interval", 2.0),
            model_version=CONFIG["yandex"].get("model_version", "latest"),
            grpc_metadata=[],
        )
    else:
        logger.debug("Using Dummy embeddings provider.")
        def dummy_embed(texts: List[str]) -> List[List[float]]:
            return [[0.0] * CONFIG["embedding"]["dim"] for _ in texts]
        return CustomEmbeddings(dummy_embed)

    

def embed_documents(docs: Union[Document, List[Document]]) -> Tuple[List[dict], Optional[str]]:
    if isinstance(docs, Document):
        docs = [docs]    

    provider = CONFIG.get("embedding", {}).get("provider", "fake")

    try:

        if provider == "yandex":
            if not YandexGPTEmbeddings:
                raise ImportError("YandexGPTEmbeddings not available. Please install langchain-community")
            logger.debug("Using YandexGPT embeddings provider.")
            api_key = CONFIG["yandex"]["api_key"]
            folder_id = CONFIG["yandex"]["folder_id"]
            disable_request_logging = CONFIG["yandex"].get("disable_request_logging", False)
            sleep_interval = CONFIG["yandex"].get("sleep_interval", 2.0)
            doc_model_name = CONFIG["yandex"].get("doc_model_name", "text-search-doc")
            model_version = CONFIG["yandex"].get("model_version", "latest")
            embedder = YandexGPTEmbeddings(
                api_key=api_key,
                folder_id=folder_id,
                grpc_metadata=[],
                disable_request_logging=disable_request_logging,
                sleep_interval=sleep_interval,
                doc_model_name=doc_model_name,   # Embedding for document chunks
                model_version=model_version,
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

        return embedded, None

    except Exception as e:
        error_message = f"Embedding error: {e}"
        logger.error(error_message)
        logger.debug(traceback.format_exc())
        return [], error_message