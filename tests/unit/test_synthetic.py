from stackshift.eval.synthetic import synthetic_proxy_notice


def test_synthetic_proxy_is_explicitly_labeled() -> None:
    notice = synthetic_proxy_notice()
    assert notice["metric_mode"] == "synthetic-proxy"
    assert "Proxy" in notice["warning"]
