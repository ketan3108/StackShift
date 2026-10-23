"""Neighbor-overlap ARR evaluation."""

from stackshift.eval.metrics import neighbor_overlap


def average_retrieval_recovery(reference: list[list[str]], observed: list[list[str]]) -> float:
    if len(reference) != len(observed) or not reference:
        raise ValueError("non-empty aligned result lists required")
    return sum(
        neighbor_overlap(left, right) for left, right in zip(reference, observed, strict=True)
    ) / len(reference)
