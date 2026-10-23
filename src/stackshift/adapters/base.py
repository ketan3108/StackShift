"""Vector adapter contract and normalization helpers."""

from typing import Protocol

import numpy as np
from numpy.typing import NDArray


def l2_normalize(vectors: NDArray[np.float32]) -> NDArray[np.float32]:
    array = np.asarray(vectors, dtype=np.float32)
    if array.ndim != 2:
        raise ValueError("vectors must be a rank-2 array")
    norms = np.linalg.norm(array, axis=1, keepdims=True)
    return (array / np.where(norms == 0.0, 1.0, norms)).astype(np.float32)


class AdapterProtocol(Protocol):
    old_dimensions: int
    new_dimensions: int

    def transform(self, vectors: NDArray[np.float32]) -> NDArray[np.float32]: ...
