"""Deterministic, leakage-safe document-set splitting."""

import random
from collections.abc import Iterable
from dataclasses import dataclass

from stackshift.errors import LeakageError


def assert_disjoint(*sets: Iterable[str]) -> None:
    normalized = [set(group) for group in sets]
    for index, left in enumerate(normalized):
        for right in normalized[index + 1 :]:
            overlap = left & right
            if overlap:
                raise LeakageError(
                    f"Document-set leakage detected: {', '.join(sorted(overlap)[:10])}"
                )


@dataclass(frozen=True)
class Split:
    train_ids: tuple[str, ...]
    validation_ids: tuple[str, ...]


def deterministic_split(ids: Iterable[str], seed: int = 42, train_fraction: float = 0.8) -> Split:
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must be between zero and one")
    shuffled = list(dict.fromkeys(ids))
    if len(shuffled) < 2:
        raise ValueError("at least two document IDs are required")
    random.Random(seed).shuffle(shuffled)
    boundary = max(1, min(len(shuffled) - 1, round(len(shuffled) * train_fraction)))
    result = Split(tuple(shuffled[:boundary]), tuple(shuffled[boundary:]))
    assert_disjoint(result.train_ids, result.validation_ids)
    return result


def enforce_evaluation_isolation(
    train_ids: Iterable[str], eval_query_ids: Iterable[str], candidate_ids: Iterable[str]
) -> None:
    assert_disjoint(train_ids, eval_query_ids, candidate_ids)
