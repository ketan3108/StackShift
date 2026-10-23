"""Vector-store contract and a safe in-memory implementation."""

from collections.abc import Sequence
from typing import Protocol

import numpy as np
from numpy.typing import NDArray


class VectorStoreProtocol(Protocol):
    """Minimum operations required by pairing, evaluation, and query routing."""

    def sample(self, count: int, seed: int = 42) -> list[str]: ...
    def read_vectors(self, ids: Sequence[str]) -> NDArray[np.float32]: ...
    def fetch_text(self, ids: Sequence[str]) -> list[str]: ...
    def search(self, vector: NDArray[np.float32], limit: int) -> list[str]: ...
    def detect_quantization(self) -> bool: ...


class InMemoryVectorStore:
    """Cosine-searchable store for tests, demos, and SDK integration examples."""

    def __init__(self, vectors: dict[str, NDArray[np.float32]], texts: dict[str, str]) -> None:
        self.vectors, self.texts = vectors, texts

    def sample(self, count: int, seed: int = 42) -> list[str]:
        return sorted(self.vectors)[:count]

    def read_vectors(self, ids: Sequence[str]) -> NDArray[np.float32]:
        return np.asarray([self.vectors[item] for item in ids], dtype=np.float32)

    def fetch_text(self, ids: Sequence[str]) -> list[str]:
        return [self.texts[item] for item in ids]

    def search(self, vector: NDArray[np.float32], limit: int) -> list[str]:
        scores = {key: float(value @ vector) for key, value in self.vectors.items()}
        return sorted(scores, key=scores.__getitem__, reverse=True)[:limit]

    def detect_quantization(self) -> bool:
        return False
