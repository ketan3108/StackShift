# ADR-0001: Python and uv tooling

## Status

Accepted.

## Decision

Use Python 3.11+ with uv, a src layout, Ruff, mypy strict, pytest, and Hatchling.

## Rationale

The model ecosystem and numerical libraries are mature in Python, while uv supports repeatable local environments and lock files.
