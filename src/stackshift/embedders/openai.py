"""OpenAI embedding backend; credentials are read only from the environment."""

import os
import random
import time
from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray


class OpenAIEmbedder:
    def __init__(
        self,
        model_id: str,
        dimensions: int | None = None,
        batch_size: int = 128,
        max_retries: int = 4,
    ) -> None:
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY must be set")
        try:
            from openai import OpenAI
        except ImportError as error:
            raise ImportError("Install OpenAI support: pip install 'stackshift[openai]'") from error
        self.model_id, self.dimensions, self.batch_size, self.max_retries = (
            model_id,
            dimensions,
            batch_size,
            max_retries,
        )
        self._client: Any = OpenAI()

    def embed(self, texts: Sequence[str]) -> NDArray[np.float32]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), self.batch_size):
            for attempt in range(self.max_retries):
                try:
                    response: Any = self._client.embeddings.create(
                        model=self.model_id,
                        input=list(texts[start : start + self.batch_size]),
                        dimensions=self.dimensions,
                    )
                    vectors.extend(item.embedding for item in response.data)
                    break
                except Exception:
                    if attempt == self.max_retries - 1:
                        raise
                    time.sleep((2**attempt) + random.random())
        return np.asarray(vectors, dtype=np.float32)
