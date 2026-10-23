import numpy as np
import torch

from stackshift.adapters.factory import train_all
from stackshift.adapters.torch_training import TorchResidual, seed_everything, train_module


def test_torch_training_is_deterministic_and_rectangular() -> None:
    rng = np.random.default_rng(7)
    new = rng.normal(size=(20, 3)).astype(np.float32)
    old = np.pad(new, ((0, 0), (0, 2))).astype(np.float32)
    seed_everything(5)
    one = TorchResidual.initialized(old, new)
    stats_one = train_module(one, old, new, seed=5, epochs=3)
    seed_everything(5)
    two = TorchResidual.initialized(old, new)
    stats_two = train_module(two, old, new, seed=5, epochs=3)
    assert stats_one.seed == stats_two.seed == 5
    assert torch.allclose(one.projection.weight, two.projection.weight)
    assert one(torch.tensor(new)).shape == (20, 5)
    trained = train_all(old, new, seed=5)
    assert trained.procrustes.old_dimensions == 5
    assert trained.lowrank(torch.tensor(new)).shape == (20, 5)
