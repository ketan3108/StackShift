from pathlib import Path

import pytest
from typer.testing import CliRunner

from stackshift.audit import write_audit_event
from stackshift.cli.app import app
from stackshift.config import StackShiftSettings
from stackshift.logging import redact_secrets


def test_version_and_help_are_available() -> None:
    runner = CliRunner()
    assert runner.invoke(app, ["--version"]).exit_code == 0
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "cutover" in result.output


def test_scan_command_is_available() -> None:
    result = CliRunner().invoke(app, ["scan"])
    assert result.exit_code == 0
    assert "metric_mode" in result.output


def test_ttl_bounds_are_validated() -> None:
    assert StackShiftSettings().state_ttl_seconds == 15
    with pytest.raises(ValueError):
        StackShiftSettings(state_ttl_seconds=31)


def test_redacts_key_fields_and_values() -> None:
    redacted = redact_secrets(None, "info", {"api_key": "x", "detail": "token sk-secret123456789"})
    assert redacted["api_key"] == "[REDACTED]"
    assert "sk-secret" not in str(redacted)


def test_audit_writes_json_line(tmp_path: Path) -> None:
    destination = tmp_path / "audit.jsonl"
    write_audit_event(destination, "train", {"adapter": "v1"})
    assert '"action": "train"' in destination.read_text(encoding="utf-8")
