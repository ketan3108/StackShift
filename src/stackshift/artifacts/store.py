"""Safetensors adapter artifacts with manifest and legacy migration support."""

import hashlib
import json
import warnings
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from safetensors.numpy import load_file, save_file

from stackshift.errors import ArtifactIntegrityError


@dataclass(frozen=True)
class ArtifactMetadata:
    version: str
    old_model_id: str
    new_model_id: str
    old_dimensions: int
    new_dimensions: int
    created_at: str
    sha256: str = ""
    normalization: bool = True
    format: str = "safetensors"


def save_artifact(
    directory: Path, version: str, matrix: NDArray[np.float32], old_model_id: str, new_model_id: str
) -> ArtifactMetadata:
    directory.mkdir(parents=True, exist_ok=True)
    weights = directory / f"{version}.safetensors"
    save_file({"matrix": np.asarray(matrix, dtype=np.float32)}, str(weights))
    digest = hashlib.sha256(weights.read_bytes()).hexdigest()
    meta = ArtifactMetadata(
        version,
        old_model_id,
        new_model_id,
        int(matrix.shape[0]),
        int(matrix.shape[1]),
        datetime.now(UTC).isoformat(),
        digest,
    )
    (directory / f"{version}.json").write_text(
        json.dumps(asdict(meta), sort_keys=True), encoding="utf-8"
    )
    return meta


def load_artifact(directory: Path, version: str) -> tuple[ArtifactMetadata, NDArray[np.float32]]:
    manifest = directory / f"{version}.json"
    meta = ArtifactMetadata(**json.loads(manifest.read_text(encoding="utf-8")))
    weights = directory / f"{version}.safetensors"
    if not weights.exists():
        legacy = directory / f"{version}.npy"
        if not legacy.exists():
            raise ArtifactIntegrityError("artifact weights are missing")
        warnings.warn(
            "legacy .npy artifact loaded; migrate to safetensors", DeprecationWarning, stacklevel=2
        )
        matrix = np.load(legacy, allow_pickle=False).astype(np.float32)
    else:
        if hashlib.sha256(weights.read_bytes()).hexdigest() != meta.sha256:
            raise ArtifactIntegrityError("artifact hash verification failed")
        matrix = load_file(str(weights))["matrix"].astype(np.float32)
    if matrix.shape != (meta.old_dimensions, meta.new_dimensions):
        raise ArtifactIntegrityError("artifact dimensions do not match metadata")
    return meta, matrix
