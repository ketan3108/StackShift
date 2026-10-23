.PHONY: setup lint format type test claims build

setup:
	uv sync --all-extras
lint:
	uv run --all-extras ruff check src tests scripts
format:
	uv run --all-extras ruff format --check src tests scripts
type:
	uv run --all-extras mypy src
test:
	uv run --all-extras pytest
claims:
	uv run --all-extras python scripts/check_claims.py
build:
	uv build
