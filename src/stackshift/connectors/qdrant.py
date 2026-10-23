"""Qdrant vector-store connector."""

from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray

from stackshift.errors import QuantizedVectorsError


class QdrantVectorStore:
    def __init__(
        self, url: str, collection: str, text_field: str = "text", api_key: str | None = None
    ) -> None:
        try:
            from qdrant_client import QdrantClient
        except ImportError as error:
            raise ImportError("Install Qdrant support: pip install 'stackshift[qdrant]'") from error
        self.client, self.collection, self.text_field = (
            QdrantClient(url=url, api_key=api_key),
            collection,
            text_field,
        )

    def detect_quantization(self) -> bool:
        info = self.client.get_collection(self.collection)
        config = info.config.params
        return bool(getattr(config, "quantization_config", None))

    def _check(self) -> None:
        if self.detect_quantization():
            raise QuantizedVectorsError("Qdrant collection uses vector quantization")

    def sample(self, count: int, seed: int = 42) -> list[str]:
        self._check()
        points, _ = self.client.scroll(
            self.collection, limit=count, with_vectors=False, with_payload=False
        )
        return [str(point.id) for point in points]

    def _points(self, ids: Sequence[str], vectors: bool) -> Any:
        return self.client.retrieve(
            self.collection, ids=list(ids), with_vectors=vectors, with_payload=True
        )

    def fetch_text(self, ids: Sequence[str]) -> list[str]:
        return [str(point.payload[self.text_field]) for point in self._points(ids, False)]

    def read_vectors(self, ids: Sequence[str]) -> NDArray[np.float32]:
        self._check()
        return np.asarray([point.vector for point in self._points(ids, True)], dtype=np.float32)

    def search(self, vector: NDArray[np.float32], limit: int) -> list[str]:
        self._check()
        return [
            str(item.id)
            for item in self.client.query_points(
                self.collection, query=vector.tolist(), limit=limit
            ).points
        ]
