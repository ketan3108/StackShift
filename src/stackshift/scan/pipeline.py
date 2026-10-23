"""Scan scoring and recommendation primitives."""

from dataclasses import dataclass

from stackshift.eval.neighbor_overlap import average_retrieval_recovery


@dataclass(frozen=True)
class ScanResult:
    arr: float
    candidate_pool_size: int
    recommendation: str
    metric_mode: str = "neighbor-overlap"


def evaluate_overlap(
    reference: list[list[str]], adapter: list[list[str]], candidate_pool_size: int
) -> ScanResult:
    arr = average_retrieval_recovery(reference, adapter)
    recommendation = "adapter-migration" if arr >= 0.95 else "full-reembed"
    return ScanResult(arr, candidate_pool_size, recommendation)
