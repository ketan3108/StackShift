"""Query routing for direct and adapter modes."""

import numpy as np
from numpy.typing import NDArray

from stackshift.adapters.base import AdapterProtocol
from stackshift.connectors.base import VectorStoreProtocol
from stackshift.embedders.base import EmbedderProtocol
from stackshift.query.state import CachedStateReader


class QueryRouter:
    def __init__(
        self,
        embedder: EmbedderProtocol,
        store: VectorStoreProtocol,
        state: CachedStateReader,
        adapter: AdapterProtocol | None = None,
    ) -> None:
        self.embedder, self.store, self.state, self.adapter = embedder, store, state, adapter

    def search(self, query: str, limit: int = 10) -> list[str]:
        vector: NDArray[np.float32] = self.embedder.embed([query])
        if self.state.get().active_mode == "adapter":
            if self.adapter is None:
                raise RuntimeError("adapter mode selected without loaded adapter")
            vector = self.adapter.transform(vector)
        return self.store.search(vector[0], limit)
