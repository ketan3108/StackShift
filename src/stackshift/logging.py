"""Structured logging with conservative secret redaction."""

import re
from collections.abc import Mapping, MutableMapping
from typing import Any, cast

import structlog

_SECRET_KEY = re.compile(r"(api[_-]?key|authorization|token|password|secret)", re.IGNORECASE)
_OPENAI_KEY = re.compile(r"sk-[A-Za-z0-9_-]{12,}")


def redact_secrets(_: Any, __: str, event_dict: MutableMapping[str, Any]) -> Mapping[str, Any]:
    """Redact known secret fields and OpenAI-style API keys recursively."""
    for key, value in list(event_dict.items()):
        if _SECRET_KEY.search(key):
            event_dict[key] = "[REDACTED]"
        elif isinstance(value, str):
            event_dict[key] = _OPENAI_KEY.sub("[REDACTED]", value)
    return event_dict


def configure_logging(run_id: str) -> structlog.stdlib.BoundLogger:
    """Configure JSON logs and bind a run identifier."""
    structlog.configure(
        processors=[
            redact_secrets,
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),
    )
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger().bind(run_id=run_id))
