"""Scan scoring and typed output with threshold provenance."""

from dataclasses import dataclass
from pathlib import Path

from stackshift.eval.neighbor_overlap import average_retrieval_recovery
from stackshift.scan.recommend import Recommendation, recommend
from stackshift.scan.thresholds import ThresholdConfig


@dataclass(frozen=True)
class ScanResult:
    arr: float
    candidate_pool_size: int
    metric_mode: str
    labeled_ndcg_retention: float | None
    recommendation: Recommendation


def evaluate_overlap(
    reference: list[list[str]],
    adapter: list[list[str]],
    candidate_pool_size: int,
    labeled_ndcg_retention: float | None = None,
    threshold_path: Path | None = None,
) -> ScanResult:
    thresholds = ThresholdConfig.load(threshold_path)
    arr = average_retrieval_recovery(reference, adapter)
    return ScanResult(
        arr,
        candidate_pool_size,
        "neighbor-overlap",
        labeled_ndcg_retention,
        recommend(arr, thresholds, labeled_ndcg_retention),
    )
