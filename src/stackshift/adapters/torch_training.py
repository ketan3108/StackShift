"""PyTorch deterministic adapter training utilities."""

import random
from dataclasses import dataclass

import numpy as np
import torch
from numpy.typing import NDArray

from stackshift.adapters.procrustes import ProcrustesAdapter


@dataclass(frozen=True)
class TrainingStats:
    seed: int
    pairs: int
    best_epoch: int
    best_validation_mse: float
    losses: tuple[float, ...]


def seed_everything(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)


def train_module(
    module: torch.nn.Module,
    old: NDArray[np.float32],
    new: NDArray[np.float32],
    seed: int = 42,
    epochs: int = 50,
    patience: int = 5,
) -> TrainingStats:
    seed_everything(seed)
    source, target = torch.tensor(new), torch.tensor(old)
    split = max(1, int(len(source) * 0.8))
    optimizer = torch.optim.AdamW(module.parameters(), lr=3e-4, weight_decay=0.01)
    best, best_state, waiting, losses = float("inf"), None, 0, []
    for _epoch in range(epochs):
        module.train()
        optimizer.zero_grad()
        loss = torch.nn.functional.mse_loss(module(source[:split]), target[:split])
        loss.backward()  # type: ignore[no-untyped-call]
        optimizer.step()
        module.eval()
        with torch.no_grad():
            validation = (
                float(torch.nn.functional.mse_loss(module(source[split:]), target[split:]))
                if split < len(source)
                else float(loss)
            )
        losses.append(validation)
        if validation < best:
            best, best_state, waiting = (
                validation,
                {k: v.detach().clone() for k, v in module.state_dict().items()},
                0,
            )
        else:
            waiting += 1
        if waiting >= patience:
            break
    if best_state is not None:
        module.load_state_dict(best_state)
    return TrainingStats(seed, len(source), len(losses) - 1, best, tuple(losses))


class TorchResidual(torch.nn.Module):
    def __init__(self, old_dim: int, new_dim: int) -> None:
        super().__init__()
        self.projection = torch.nn.Linear(new_dim, old_dim, bias=False)
        self.hidden = torch.nn.Linear(old_dim, 256)
        self.out = torch.nn.Linear(256, old_dim)
        self.dropout = torch.nn.Dropout(0.1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        projected = self.projection(x)
        return projected + self.out(self.dropout(torch.nn.functional.gelu(self.hidden(projected))))  # type: ignore[no-any-return]

    @classmethod
    def initialized(cls, old: NDArray[np.float32], new: NDArray[np.float32]) -> "TorchResidual":
        item = cls(old.shape[1], new.shape[1])
        item.projection.weight.data.copy_(torch.tensor(ProcrustesAdapter.fit(old, new).matrix))
        return item
