"""Retrieval metrics that keep unlabeled overlap separate from labeled quality."""

import math
from collections.abc import Iterable


def neighbor_overlap(reference: Iterable[str], observed: Iterable[str]) -> float:
    expected, actual = set(reference), set(observed)
    return len(expected & actual) / len(expected) if expected else 0.0


def recall_at_k(retrieved: Iterable[str], relevant: set[str]) -> float:
    return len(set(retrieved) & relevant) / len(relevant) if relevant else 0.0


def ndcg_at_k(retrieved: Iterable[str], relevant: set[str]) -> float:
    ideal = sum(
        1 / math.log2(index + 2) for index in range(min(len(relevant), len(list(retrieved))))
    )
    items = list(retrieved)
    score = sum(1 / math.log2(index + 2) for index, item in enumerate(items) if item in relevant)
    return score / ideal if ideal else 0.0


def retention(adapter: float, direct: float) -> float:
    return adapter / direct if direct else 0.0
