from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from readservice.utils.logger import get_logger
from .base import BaseEmbedder
import json

logger = get_logger()


class YandexOpenAIEmbeddings(OpenAIEmbeddings):
    def __init__(self, folder_id=None, api_key=None, **kwargs):
        super().__init__(**kwargs)
        self._yandex_folder_id = folder_id
        self._yandex_api_key = api_key

    @property
    def _invocation_params(self):
        base = super()._invocation_params
        base = dict(base)  # Ensure it's mutable

        # Inject custom params via `user` field
        base["user"] = json.dumps({
            "folder_id": self._yandex_folder_id,
            "api_key": self._yandex_api_key
        })

        return base


class LiteLLMEmbedder(BaseEmbedder):
    def __init__(self, cfg: dict):
        self.cfg = cfg
        logger.debug("Using YandexOpenAIEmbeddings with LiteLLM proxy.")

    def get_embedding_function(self):
        return YandexOpenAIEmbeddings(
            model=self.cfg.get("model", "yandex-embedding"),
            openai_api_base=self.cfg.get("api_base", "http://localhost:4000"),
            openai_api_key="unused",  # Required by LangChain but ignored by LiteLLM
            folder_id=self.cfg.get("folder_id"),
            api_key=self.cfg.get("api_key"),
        )

    def embed_documents(self, docs: list[Document]) -> list[dict]:
        embedder = self.get_embedding_function()
        vectors = embedder.embed_documents([doc.page_content for doc in docs])
        return [
            {"embedding": vec, "metadata": doc.metadata}
            for doc, vec in zip(docs, vectors)
        ]
