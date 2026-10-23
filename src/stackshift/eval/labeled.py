"""Labeled retrieval retention evaluation."""

from stackshift.eval.metrics import ndcg_at_k, recall_at_k, retention


def labeled_retention(
    adapter: list[str], direct: list[str], relevant: set[str]
) -> dict[str, float]:
    return {
        "ndcg_at_10_retention": retention(
            ndcg_at_k(adapter[:10], relevant), ndcg_at_k(direct[:10], relevant)
        ),
        "recall_at_10_retention": retention(
            recall_at_k(adapter[:10], relevant), recall_at_k(direct[:10], relevant)
        ),
    }
