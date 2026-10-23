"""FAISS connector. Quantized indexes are deliberately rejected."""

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray

from stackshift.errors import QuantizedVectorsError


class FaissVectorStore:
    def __init__(
        self, index: Any, ids: Sequence[str], doc_id_to_text: Callable[[str], str]
    ) -> None:
        self.index, self.ids, self.doc_id_to_text = index, list(ids), doc_id_to_text

    def detect_quantization(self) -> bool:
        name = type(self.index).__name__.lower()
        return any(token in name for token in ("pq", "sq", "binary"))

    def _check(self) -> None:
        if self.detect_quantization():
            raise QuantizedVectorsError("FAISS PQ/SQ/binary index is not full precision")

    def sample(self, count: int, seed: int = 42) -> list[str]:
        self._check()
        return self.ids[:count]

    def fetch_text(self, ids: Sequence[str]) -> list[str]:
        return [self.doc_id_to_text(item) for item in ids]

    def read_vectors(self, ids: Sequence[str]) -> NDArray[np.float32]:
        self._check()
        return np.asarray(
            [self.index.reconstruct(self.ids.index(item)) for item in ids], dtype=np.float32
        )

    def search(self, vector: NDArray[np.float32], limit: int) -> list[str]:
        self._check()
        _, indices = self.index.search(np.asarray([vector], dtype=np.float32), limit)
        return [self.ids[i] for i in indices[0] if i >= 0]
