from pathlib import Path
import numpy as np
from stackshift.adapters.lowrank_affine import LowRankAffineAdapter
from stackshift.adapters.procrustes import ProcrustesAdapter
from stackshift.adapters.residual_mlp import ResidualMLPAdapter
from stackshift.artifacts.store import load_artifact, save_artifact
from stackshift.connectors.base import InMemoryVectorStore
from stackshift.embedders.base import HashEmbedder
from stackshift.eval.labeled import labeled_retention
from stackshift.eval.metrics import ndcg_at_k, neighbor_overlap, recall_at_k, retention
from stackshift.eval.neighbor_overlap import average_retrieval_recovery
from stackshift.pairing import PairingBuilder
from stackshift.query.router import QueryRouter
from stackshift.query.state import CachedStateReader, FileStateBackend, LiveState
from stackshift.scan.pipeline import evaluate_overlap


def test_core_end_to_end(tmp_path: Path) -> None:
    ids = [str(index) for index in range(10)]
    embedder = HashEmbedder(8)
    vectors = embedder.embed([f"document {identifier}" for identifier in ids])
    store = InMemoryVectorStore(
        dict(zip(ids, vectors, strict=True)),
        {identifier: f"document {identifier}" for identifier in ids},
    )
    pairs = PairingBuilder(sample_size=10).build(store, embedder, "old")
    adapter = ProcrustesAdapter.fit(pairs.train_old, pairs.train_new)
    assert adapter.orthogonality_error() < 1e-5
    assert adapter.transform(pairs.validation_new).shape[1] == 8
    assert (
        LowRankAffineAdapter.fit(pairs.train_old, pairs.train_new)
        .transform(pairs.validation_new)
        .shape[1]
        == 8
    )
    assert (
        ResidualMLPAdapter.fit(pairs.train_old, pairs.train_new)
        .transform(pairs.validation_new)
        .shape[1]
        == 8
    )
    meta = save_artifact(tmp_path, "v1", adapter.matrix, "old", "new")
    loaded, matrix = load_artifact(tmp_path, "v1")
    assert loaded.sha256 == meta.sha256 and matrix.shape == (8, 8)
    state_path = tmp_path / "state.json"
    backend = FileStateBackend(str(state_path))
    backend.write(LiveState("adapter", "v1"))
    router = QueryRouter(embedder, store, CachedStateReader(backend, 5), adapter)
    assert router.search("document 1", 3)
    assert average_retrieval_recovery([["a"]], [["a"]]) == 1.0
    assert evaluate_overlap([["a"]], [["a"]], 10).recommendation == "adapter-migration"
    assert (
        neighbor_overlap(["a"], ["a"])
        == recall_at_k(["a"], {"a"})
        == ndcg_at_k(["a"], {"a"})
        == retention(1.0, 1.0)
    )
