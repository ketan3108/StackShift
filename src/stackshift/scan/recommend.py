"""Explainable scan recommendations based on versioned provisional thresholds."""

from dataclasses import dataclass

from stackshift.scan.thresholds import ThresholdConfig


@dataclass(frozen=True)
class Recommendation:
    decision: str
    reasons: tuple[str, ...]
    threshold_status: str
    threshold_provenance: str
    calibrated_from: str


def recommend(
    arr: float, thresholds: ThresholdConfig, labeled_ndcg_retention: float | None = None
) -> Recommendation:
    reasons: list[str] = [f"Neighbor-overlap ARR: {arr:.3f}."]
    if arr < thresholds.neighbor_overlap_drastic_drift_floor:
        reasons.append("ARR is below the drastic-drift floor.")
        decision = "full-reembed"
    elif (
        labeled_ndcg_retention is not None
        and labeled_ndcg_retention < thresholds.labeled_retention_minimum
    ):
        reasons.append("Labeled nDCG@10 retention is below the minimum floor.")
        decision = "full-reembed"
    elif arr < thresholds.neighbor_overlap_adapter_floor:
        reasons.append("ARR is below the provisional adapter floor.")
        decision = "full-reembed"
    elif (
        labeled_ndcg_retention is not None
        and labeled_ndcg_retention < thresholds.labeled_retention_adapter_floor
    ):
        reasons.append("Labeled nDCG@10 retention is below the preferred adapter floor.")
        decision = "full-reembed"
    else:
        reasons.append("All available measurements meet provisional adapter criteria.")
        decision = "adapter-migration"
    return Recommendation(
        decision,
        tuple(reasons),
        thresholds.status,
        thresholds.provenance,
        thresholds.calibrated_from,
    )
