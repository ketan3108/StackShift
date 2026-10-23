"""Remote-live-state abstractions with TTL fail-safe cache."""

from dataclasses import dataclass
from time import monotonic
from typing import Protocol

from stackshift.errors import StateUnavailableError


@dataclass(frozen=True)
class LiveState:
    active_mode: str = "direct"
    adapter_version: str | None = None


class StateBackend(Protocol):
    def read(self) -> LiveState: ...
    def write(self, state: LiveState) -> None: ...


class FileStateBackend:
    def __init__(self, path: str) -> None:
        self.path = path

    def read(self) -> LiveState:
        import json

        try:
            with open(self.path, encoding="utf-8") as file:
                return LiveState(**json.load(file))
        except OSError as error:
            raise StateUnavailableError(str(error)) from error

    def write(self, state: LiveState) -> None:
        import json
        import os

        temporary = f"{self.path}.tmp"
        with open(temporary, "w", encoding="utf-8") as file:
            json.dump(state.__dict__, file)
        os.replace(temporary, self.path)


class CachedStateReader:
    def __init__(self, backend: StateBackend, ttl_seconds: int = 15) -> None:
        if not 5 <= ttl_seconds <= 30:
            raise ValueError("TTL must be between 5 and 30 seconds")
        self.backend, self.ttl_seconds, self._cached, self._at = (
            backend,
            ttl_seconds,
            LiveState(),
            0.0,
        )

    def get(self) -> LiveState:
        if monotonic() - self._at < self.ttl_seconds:
            return self._cached
        try:
            self._cached = self.backend.read()
            self._at = monotonic()
        except StateUnavailableError:
            pass
        return self._cached
