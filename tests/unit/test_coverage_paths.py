from pathlib import Path

import numpy as np
import pytest
from typer.testing import CliRunner

from stackshift.adapters.base import l2_normalize
from stackshift.adapters.lowrank_affine import LowRankAffineAdapter
from stackshift.adapters.procrustes import ProcrustesAdapter
from stackshift.adapters.residual_mlp import ResidualMLPAdapter
from stackshift.artifacts.store import load_artifact, save_artifact
from stackshift.cli.app import app
from stackshift.embedders.base import HashEmbedder
from stackshift.errors import (
    ArtifactIntegrityError,
    MissingTextError,
    QuantizedVectorsError,
    StateUnavailableError,
)
from stackshift.eval.labeled import labeled_retention
from stackshift.eval.neighbor_overlap import average_retrieval_recovery
from stackshift.pairing import PairingBuilder
from stackshift.query.state import CachedStateReader, FileStateBackend
from stackshift.scan.pipeline import evaluate_overlap
from stackshift.splits import deterministic_split


class BadStore:
    def __init__(self, quantized: bool = False, missing: bool = False) -> None:
        self.quantized, self.missing = quantized, missing

    def detect_quantization(self) -> bool:
        return self.quantized

    def sample(self, count: int, seed: int = 42) -> list[str]:
        return [str(i) for i in range(10)]

    def fetch_text(self, ids: list[str]) -> list[str]:
        if self.missing:
            raise KeyError("x")
        return ids

    def read_vectors(self, ids: list[str]) -> np.ndarray:
        return np.ones((len(ids), 3), dtype=np.float32)


def test_pairing_preconditions_and_split_edges() -> None:
    embedder = HashEmbedder(3)
    with pytest.raises(QuantizedVectorsError):
        PairingBuilder(10).build(BadStore(quantized=True), embedder, "old")
    with pytest.raises(MissingTextError):
        PairingBuilder(10).build(BadStore(missing=True), embedder, "old")
    with pytest.raises(ValueError):
        deterministic_split(["one"])
    with pytest.raises(ValueError):
        deterministic_split(["a", "b"], train_fraction=1)
    with pytest.raises(ValueError):
        l2_normalize(np.ones(3, dtype=np.float32))


def test_artifact_tamper_and_state_failure(tmp_path: Path) -> None:
    meta = save_artifact(tmp_path, "v", np.eye(3, dtype=np.float32), "old", "new")
    file = tmp_path / "v.safetensors"
    file.write_bytes(file.read_bytes() + b"tamper")
    with pytest.raises(ArtifactIntegrityError):
        load_artifact(tmp_path, meta.version)
    backend = FileStateBackend(str(tmp_path / "missing.json"))
    with pytest.raises(StateUnavailableError):
        backend.read()
    assert CachedStateReader(backend, 5).get().active_mode == "direct"
    with pytest.raises(ValueError):
        CachedStateReader(backend, 4)


def test_adapter_and_metric_error_paths() -> None:
    adapter = ProcrustesAdapter.fit(np.eye(3, dtype=np.float32), np.eye(3, dtype=np.float32))
    with pytest.raises(ValueError):
        adapter.transform(np.ones((1, 4), dtype=np.float32))
    with pytest.raises(ValueError):
        average_retrieval_recovery([], [])
    assert labeled_retention(["a"], ["a"], {"a"})["recall_at_10_retention"] == 1
    assert (
        evaluate_overlap([["a"]], [["a"]], 2, labeled_ndcg_retention=0.80).recommendation.decision
        == "full-reembed"
    )


def test_all_cli_paths(tmp_path: Path) -> None:
    runner = CliRunner()
    for command in ("scan", "train", "validate", "ingest", "report"):
        assert runner.invoke(app, [command, "--json"]).exit_code == 0
    assert runner.invoke(app, ["rollback", str(tmp_path / "s.json")]).exit_code != 0
    matrix = np.eye(2, dtype=np.float32)
    save_artifact(tmp_path, "v", matrix, "old", "new")
    state = tmp_path / "state.json"
    assert (
        runner.invoke(
            app, ["cutover", str(state), "v", "--artifacts", str(tmp_path), "--yes"]
        ).exit_code
        == 0
    )
    assert runner.invoke(app, ["rollback", str(state), "--yes", "--json"]).exit_code == 0


def test_adapter_properties_and_pairing_remaining_paths() -> None:
    old = np.eye(3, dtype=np.float32)
    new = np.eye(3, dtype=np.float32)
    low_rank = LowRankAffineAdapter.fit(old, new)
    residual = ResidualMLPAdapter.fit(old, new)
    assert low_rank.old_dimensions == low_rank.new_dimensions == 3
    assert residual.old_dimensions == residual.new_dimensions == 3
    with pytest.raises(ValueError):
        low_rank.transform(np.ones((1, 4), dtype=np.float32))
    with pytest.raises(ValueError):
        residual.transform(np.ones((1, 4), dtype=np.float32))
    with pytest.raises(ValueError):
        PairingBuilder(9)

    class SmallStore(BadStore):
        def sample(self, count: int, seed: int = 42) -> list[str]:
            return ["one"]

    with pytest.raises(ValueError):
        PairingBuilder(10).build(SmallStore(), HashEmbedder(3), "old")

    class EmptyTextStore(BadStore):
        def fetch_text(self, ids: list[str]) -> list[str]:
            return [""] * len(ids)

    with pytest.raises(MissingTextError):
        PairingBuilder(10).build(EmptyTextStore(), HashEmbedder(3), "old")


def test_procrustes_fit_rejects_invalid_pair_count() -> None:
    with pytest.raises(ValueError):
        ProcrustesAdapter.fit(np.ones((1, 2), dtype=np.float32), np.ones((1, 2), dtype=np.float32))
