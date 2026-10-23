import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from stackshift.adapters.base import l2_normalize
from stackshift.adapters.procrustes import ProcrustesAdapter
from stackshift.errors import LeakageError
from stackshift.scan.pipeline import evaluate_overlap
from stackshift.splits import enforce_evaluation_isolation


@given(st.integers(min_value=2, max_value=8), st.integers(min_value=2, max_value=4))
def test_normalize_invariant(rows: int, columns: int) -> None:
    array = np.arange(rows * columns, dtype=np.float32).reshape(rows, columns) - 5
    normalized = l2_normalize(array)
    norms = np.linalg.norm(normalized, axis=1)
    assert np.all((np.isclose(norms, 1.0)) | (np.isclose(norms, 0.0)))


def test_procrustes_recovers_known_square_rotation() -> None:
    rng = np.random.default_rng(3)
    new = rng.normal(size=(100, 4)).astype(np.float32)
    q, _ = np.linalg.qr(rng.normal(size=(4, 4)))
    old = new @ q.T
    adapter = ProcrustesAdapter.fit(old, new)
    assert adapter.orthogonality_error() < 1e-5
    assert np.mean(np.sum(adapter.transform(new) * l2_normalize(old), axis=1)) > 0.999


def test_procrustes_tall_and_wide_constraints() -> None:
    rng = np.random.default_rng(4)
    for old_dim, new_dim in ((6, 3), (3, 6)):
        new = rng.normal(size=(100, new_dim)).astype(np.float32)
        q, _ = np.linalg.qr(rng.normal(size=(max(old_dim, new_dim), max(old_dim, new_dim))))
        matrix = q[:old_dim, :new_dim].astype(np.float32)
        old = new @ matrix.T
        adapter = ProcrustesAdapter.fit(old, new)
        assert adapter.orthogonality_error() < 1e-5
        assert adapter.transform(new).shape == (100, old_dim)


def test_leakage_is_a_hard_failure() -> None:
    with pytest.raises(LeakageError):
        enforce_evaluation_isolation(["train"], ["train"], ["candidate"])


def test_provisional_threshold_output_and_drift_floor() -> None:
    result = evaluate_overlap([["a"]], [["b"]], 10)
    assert result.recommendation.decision == "full-reembed"
    assert result.recommendation.threshold_status == "provisional"
    assert "Gate 1" in result.recommendation.calibrated_from
