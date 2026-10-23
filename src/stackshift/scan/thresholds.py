"""Versioned, provisional recommendation thresholds."""

import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ThresholdConfig:
    status: str
    version: str
    provenance: str
    calibrated_from: str
    neighbor_overlap_adapter_floor: float
    neighbor_overlap_drastic_drift_floor: float
    labeled_retention_adapter_floor: float
    labeled_retention_minimum: float

    @classmethod
    def load(cls, path: Path | None = None) -> "ThresholdConfig":
        resolved = path or Path(__file__).parents[3] / "config" / "thresholds.toml"
        with resolved.open("rb") as source:
            return cls(**tomllib.load(source))
