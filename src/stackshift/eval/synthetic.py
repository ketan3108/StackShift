"""Optional synthetic queries, always reported as proxy metrics."""


def synthetic_proxy_notice() -> dict[str, str]:
    return {"metric_mode": "synthetic-proxy", "warning": "Proxy metric; not retrieval quality."}
