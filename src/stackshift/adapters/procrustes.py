"""Closed-form rectangular orthogonal Procrustes adapter."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from stackshift.adapters.base import l2_normalize


@dataclass(frozen=True)
class ProcrustesAdapter:
    matrix: NDArray[np.float32]

    @property
    def old_dimensions(self) -> int:
        return int(self.matrix.shape[0])

    @property
    def new_dimensions(self) -> int:
        return int(self.matrix.shape[1])

    @classmethod
    def fit(
        cls, old_vectors: NDArray[np.float32], new_vectors: NDArray[np.float32]
    ) -> "ProcrustesAdapter":
        old, new = l2_normalize(old_vectors), l2_normalize(new_vectors)
        if old.shape[0] != new.shape[0] or old.shape[0] < 2:
            raise ValueError("paired rows required")
        left, _, right_t = np.linalg.svd(old.T @ new, full_matrices=False)
        return cls((left @ right_t).astype(np.float32))

    def transform(self, vectors: NDArray[np.float32]) -> NDArray[np.float32]:
        if vectors.ndim != 2 or vectors.shape[1] != self.new_dimensions:
            raise ValueError("adapter input dimensions do not match")
        return l2_normalize(np.asarray(vectors, dtype=np.float32) @ self.matrix.T)

    def orthogonality_error(self) -> float:
        matrix = self.matrix.astype(np.float64)
        product = (
            matrix.T @ matrix if self.old_dimensions >= self.new_dimensions else matrix @ matrix.T
        )
        return float(np.max(np.abs(product - np.eye(product.shape[0]))))
