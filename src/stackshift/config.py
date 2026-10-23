"""Validated runtime settings."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class StackShiftSettings(BaseModel):
    """Settings that are safe to expose in diagnostics."""

    model_config = ConfigDict(extra="forbid")

    state_ttl_seconds: int = Field(default=15, ge=5, le=30)
    artifact_directory: Path = Path(".stackshift/artifacts")
    audit_log_path: Path = Path(".stackshift/audit.jsonl")
    include_text_in_reports: bool = False
