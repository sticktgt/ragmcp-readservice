from readservice.config import CONFIG
from .yandex import YandexEmbedder
from .dummy import CustomDummyEmbedder, LangchainFakeEmbedder
from .litellm import LiteLLMEmbedder
from .base import BaseEmbedder


def get_embedder(cfg: dict) -> BaseEmbedder:
    provider = cfg.get("provider", "fake")

    if provider == "yandex":
        return YandexEmbedder(cfg["yandex"])
    elif provider == "lite":
        return LiteLLMEmbedder(cfg["lite"])
    elif provider == "langchain_fake":
        return LangchainFakeEmbedder()
    else:
        return CustomDummyEmbedder()
