import os
import json
import aiohttp
from litellm.types.utils import EmbeddingResponse

class YandexCustomLLM:
    def __init__(self, *args, **kwargs):
        # Optional: fallback env vars
        self.folder_id = os.getenv("YANDEX_FOLDER_ID")
        self.api_key = os.getenv("YANDEX_API_KEY")

    async def aembedding(self, input, model, **kwargs):
        # Extract folder_id and api_key from `user` JSON string passed via LangChain
        user_info_str = kwargs.get("litellm_params", {}).get("metadata", {}).get("user_api_key_end_user_id", "")
        try:
            user_info = json.loads(user_info_str)
            api_key = user_info.get("api_key") or self.api_key
            folder_id = user_info.get("folder_id") or self.folder_id
        except Exception as e:
            raise Exception(f"Failed to parse folder_id/api_key from: {user_info_str}. Error: {e}")

        if not folder_id or not api_key:
            raise Exception("Missing folder_id or api_key")

        # if isinstance(input, list):
        #     input = input[0] if input else ""

        # Ensure we're working with a list of texts
        if not isinstance(input, list):
            input = [input]

        model_uri = f"emb://{folder_id}/text-search-doc/latest"
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/textEmbedding"

        headers = {
            "Authorization": f"Api-Key {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "modelUri": model_uri,
            "text": input
        }

        # Remove OpenAI-specific params
        for param in ("encoding_format", "user"):
            kwargs.pop(param, None)

        results = []
        async with aiohttp.ClientSession() as session:
            for text in input:
                payload = {
                    "modelUri": model_uri,
                    "text": text
                }

                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 200:
                        raise Exception(f"Yandex API Error: {await response.text()}")
                    result = await response.json()
                    embedding = result.get("embedding")
                    if not embedding:
                        raise Exception("No embedding in response")
                    results.append({"embedding": embedding})

        return EmbeddingResponse(data=results)


# IMPORTANT: this must match the litellm.yaml config
my_custom_llm = YandexCustomLLM()
