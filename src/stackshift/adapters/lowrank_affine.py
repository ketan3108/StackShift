"""Low-rank affine adapter with a rectangular linear map."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from stackshift.adapters.base import l2_normalize


@dataclass(frozen=True)
class LowRankAffineAdapter:
    matrix: NDArray[np.float32]
    bias: NDArray[np.float32]

    @property
    def old_dimensions(self) -> int:
        return int(self.matrix.shape[0])

    @property
    def new_dimensions(self) -> int:
        return int(self.matrix.shape[1])

    @classmethod
    def fit(
        cls, old: NDArray[np.float32], new: NDArray[np.float32], rank: int = 64
    ) -> "LowRankAffineAdapter":
        target, source = l2_normalize(old), l2_normalize(new)
        bias = (
            target.mean(axis=0) - source.mean(axis=0)[: target.shape[1]]
            if target.shape[1] == source.shape[1]
            else target.mean(axis=0)
        ).astype(np.float32)
        solution = np.linalg.lstsq(source, target - bias, rcond=None)[0].T
        left, values, right = np.linalg.svd(solution, full_matrices=False)
        keep = min(rank, len(values))
        return cls((left[:, :keep] * values[:keep]) @ right[:keep, :], bias)

    def transform(self, vectors: NDArray[np.float32]) -> NDArray[np.float32]:
        if vectors.ndim != 2 or vectors.shape[1] != self.new_dimensions:
            raise ValueError("adapter input dimensions do not match")
        return l2_normalize(np.asarray(vectors, dtype=np.float32) @ self.matrix.T + self.bias)
