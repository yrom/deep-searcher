import os
from typing import List, Union

import requests

from deepsearcher.embedding.base import BaseEmbedding

SILICONFLOW_MODEL_DIM_MAP = {
    "BAAI/bge-m3": 1024,
    "netease-youdao/bce-embedding-base_v1": 768,
    "BAAI/bge-large-zh-v1.5": 1024,
    "BAAI/bge-large-en-v1.5": 1024,
    "Pro/BAAI/bge-m3": 1024,  # paid model
}

SILICONFLOW_EMBEDDING_API = "https://api.siliconflow.cn/v1/embeddings"


class SiliconflowEmbedding(BaseEmbedding):
    """
    https://docs.siliconflow.cn/en/api-reference/embeddings/create-embeddings
    """

    def __init__(self, model="BAAI/bge-m3", batch_size=32, **kwargs):
        if "model_name" in kwargs and (not model or model == "BAAI/bge-m3"):
            model = kwargs.pop("model_name")
        self.model = model
        if "api_key" in kwargs:
            api_key = kwargs.pop("api_key")
        else:
            api_key = os.getenv("SILICONFLOW_API_KEY")

        self.api_key = api_key
        self.batch_size = batch_size

    def embed_query(self, text: str) -> List[float]:
        """
        input_type (`str`): "query" or "document" for retrieval case.
        """
        return self._embed_input(text)[0]

    def embed_documents(self, texts: list[str]) -> List[List[float]]:
        # batch embedding
        return self._embed_input(texts)

    def _embed_input(self, input: Union[str, List[str]]) -> List[List[float]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "input": input, "encoding_format": "float"}
        response = requests.request(
            "POST", SILICONFLOW_EMBEDDING_API, json=payload, headers=headers
        )
        response.raise_for_status()
        result = response.json()["data"]
        sorted_results = sorted(result, key=lambda x: x["index"])
        return [res["embedding"] for res in sorted_results]

    @property
    def dimension(self) -> int:
        return SILICONFLOW_MODEL_DIM_MAP[self.model]
