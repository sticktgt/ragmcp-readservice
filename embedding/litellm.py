from typing import List
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from .base import BaseEmbedder
from readservice.utils.logger import get_logger
import litellm

logger = get_logger()


class LiteLLMEmbeddings(Embeddings):
    def __init__(self, model: str, api_key: str, api_base: str, folder_id: str):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.folder_id = folder_id

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # logger.debug(f"[LiteLLMEmbeddings] Embedding {len(texts)} documents with model '{self.model}'")

        embeddings = []
        for text in texts:
            response = litellm.embedding(
                model=self.model,
                input=text,
                api_key=self.api_key,
                api_base=self.api_base,
                additional_args={"folder_id": self.folder_id} if self.folder_id else None,
            )
            embedding = response["data"][0]["embedding"]
            embeddings.append(embedding)

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


class LiteLLMEmbedder(BaseEmbedder):
    def __init__(self, cfg: dict):
        self.cfg = cfg
        logger.debug("Using LiteLLM embeddings provider.")

    def get_embedding_function(self) -> Embeddings:
        model = self.cfg.get("model", "")
        api_key = self.cfg.get("api_key", "")
        folder_id = self.cfg.get("folder_id", "")
        api_base = self.cfg.get("api_base", "")

        return LiteLLMEmbeddings(
            model=model,
            api_key=api_key,
            api_base=api_base,
            folder_id=folder_id,
        )

    def embed_documents(self, docs: List[Document]) -> List[dict]:
        embedder = self.get_embedding_function()
        vectors = embedder.embed_documents([doc.page_content for doc in docs])
        return [
            {"embedding": vec, "metadata": doc.metadata}
            for doc, vec in zip(docs, vectors)
        ]
