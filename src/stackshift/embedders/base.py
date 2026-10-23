"""Embedding provider interfaces and deterministic offline test provider."""

from collections.abc import Sequence
from typing import Protocol

import numpy as np
from numpy.typing import NDArray


class EmbedderProtocol(Protocol):
    model_id: str

    def embed(self, texts: Sequence[str]) -> NDArray[np.float32]: ...


class HashEmbedder:
    def __init__(self, dimensions: int = 32, model_id: str = "stackshift/hash-v1") -> None:
        if dimensions < 2:
            raise ValueError("dimensions must be at least two")
        self.dimensions, self.model_id = dimensions, model_id

    def embed(self, texts: Sequence[str]) -> NDArray[np.float32]:
        vectors = np.zeros((len(texts), self.dimensions), dtype=np.float32)
        for row, text in enumerate(texts):
            for byte in text.encode("utf-8"):
                vectors[row, byte % self.dimensions] += 1.0
        return vectors
