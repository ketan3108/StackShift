"""Trainable rectangular low-rank affine adapter."""

import torch


class TorchLowRankAffine(torch.nn.Module):
    def __init__(self, old_dim: int, new_dim: int, rank: int = 64) -> None:
        super().__init__()
        effective_rank = min(rank, old_dim, new_dim)
        self.left = torch.nn.Linear(effective_rank, old_dim, bias=False)
        self.right = torch.nn.Linear(new_dim, effective_rank, bias=False)
        self.bias = torch.nn.Parameter(torch.zeros(old_dim))
        self.old_dimensions, self.new_dimensions = old_dim, new_dim

    def forward(self, values: torch.Tensor) -> torch.Tensor:
        return self.left(self.right(values)) + self.bias  # type: ignore[no-any-return]
