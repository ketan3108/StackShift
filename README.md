# StackShift

StackShift measures behavioral drift when an embedding model changes, then helps teams decide whether an adapter migration is appropriate for their corpus.

It is local-first: corpus data stays in your environment except for explicitly configured embedding providers. StackShift has no telemetry by default.

## Status

This repository is in Phase 0 of an evidence-gated build. The public CLI shell is available, but scan, training, validation, and migration functionality are not yet implemented. Do not use this version in production.

## Intended workflow

`scan` -> `train` -> `validate` -> `cutover` -> `rollback`

See [the claims contract](docs/claims-contract.md) and [roadmap](docs/roadmap.md) before evaluating the project.

## Development

Requires Python 3.11+ and uv.

```powershell
uv sync --all-extras
uv run stackshift --help
make lint
make type
make test
```
