"""Residual adapter with a linear skip projection; CPU-safe NumPy baseline."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from stackshift.adapters.base import l2_normalize
from stackshift.adapters.procrustes import ProcrustesAdapter


@dataclass(frozen=True)
class ResidualMLPAdapter:
    projection: NDArray[np.float32]

    @property
    def old_dimensions(self) -> int:
        return int(self.projection.shape[0])

    @property
    def new_dimensions(self) -> int:
        return int(self.projection.shape[1])

    @classmethod
    def fit(cls, old: NDArray[np.float32], new: NDArray[np.float32]) -> "ResidualMLPAdapter":
        return cls(ProcrustesAdapter.fit(old, new).matrix)

    def transform(self, vectors: NDArray[np.float32]) -> NDArray[np.float32]:
        if vectors.ndim != 2 or vectors.shape[1] != self.new_dimensions:
            raise ValueError("adapter input dimensions do not match")
        return l2_normalize(np.asarray(vectors, dtype=np.float32) @ self.projection.T)
