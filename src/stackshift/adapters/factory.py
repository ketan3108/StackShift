"""Training factory for all supported adapter families."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from stackshift.adapters.procrustes import ProcrustesAdapter
from stackshift.adapters.torch_lowrank import TorchLowRankAffine
from stackshift.adapters.torch_training import TorchResidual, TrainingStats, train_module


@dataclass(frozen=True)
class TrainedAdapters:
    procrustes: ProcrustesAdapter
    residual: TorchResidual
    lowrank: TorchLowRankAffine
    residual_stats: TrainingStats
    lowrank_stats: TrainingStats


def train_all(
    old: NDArray[np.float32], new: NDArray[np.float32], seed: int = 42
) -> TrainedAdapters:
    procrustes = ProcrustesAdapter.fit(old, new)
    residual = TorchResidual.initialized(old, new)
    residual_stats = train_module(residual, old, new, seed=seed)
    lowrank = TorchLowRankAffine(old.shape[1], new.shape[1])
    lowrank_stats = train_module(lowrank, old, new, seed=seed)
    return TrainedAdapters(procrustes, residual, lowrank, residual_stats, lowrank_stats)
