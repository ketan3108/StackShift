"""Hashed adapter artifacts stored without pickle."""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

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


def save_artifact(
    directory: Path, version: str, matrix: NDArray[np.float32], old_model_id: str, new_model_id: str
) -> ArtifactMetadata:
    directory.mkdir(parents=True, exist_ok=True)
    weights = directory / f"{version}.npy"
    np.save(weights, matrix, allow_pickle=False)
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
    meta = ArtifactMetadata(
        **json.loads((directory / f"{version}.json").read_text(encoding="utf-8"))
    )
    weights = directory / f"{version}.npy"
    if not weights.exists() or hashlib.sha256(weights.read_bytes()).hexdigest() != meta.sha256:
        raise ArtifactIntegrityError("artifact hash verification failed")
    matrix = np.load(weights, allow_pickle=False).astype(np.float32)
    if matrix.shape != (meta.old_dimensions, meta.new_dimensions):
        raise ArtifactIntegrityError("artifact dimensions do not match metadata")
    return meta, matrix
