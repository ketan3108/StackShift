"""Append-only local audit log."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def write_audit_event(path: Path, action: str, details: dict[str, Any]) -> None:
    """Append a timestamped event without storing secrets or source text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {"at": datetime.now(UTC).isoformat(), "action": action, "details": details}
    with path.open("a", encoding="utf-8") as audit_file:
        audit_file.write(json.dumps(event, sort_keys=True) + "\n")
