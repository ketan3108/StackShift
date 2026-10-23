import json
from pathlib import Path

import numpy as np
import pytest

from stackshift.artifacts.store import ArtifactMetadata, load_artifact, save_artifact
from stackshift.errors import ArtifactIntegrityError


def test_safetensors_tamper_and_legacy_migration(tmp_path: Path) -> None:
    matrix = np.eye(2, dtype=np.float32)
    save_artifact(tmp_path, "safe", matrix, "old", "new")
    assert (tmp_path / "safe.safetensors").exists()
    weights = tmp_path / "safe.safetensors"
    weights.write_bytes(weights.read_bytes() + b"x")
    with pytest.raises(ArtifactIntegrityError):
        load_artifact(tmp_path, "safe")
    np.save(tmp_path / "legacy.npy", matrix, allow_pickle=False)
    legacy = ArtifactMetadata("legacy", "old", "new", 2, 2, "now")
    (tmp_path / "legacy.json").write_text(json.dumps(legacy.__dict__), encoding="utf-8")
    with pytest.deprecated_call():
        _, loaded = load_artifact(tmp_path, "legacy")
    assert np.array_equal(loaded, matrix)
