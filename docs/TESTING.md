# Manual testing and validation

| Test | Command | Expected result | Actual | Pass/Fail | Notes |
| --- | --- | --- | --- | --- | --- |
| Unit suite | `uv run --all-extras pytest` | Green coverage gate |  |  |  |
| Claims | `uv run python scripts/check_claims.py` | `Claims check passed.` |  |  |  |
| Package | `uv build` | wheel and sdist in `dist/` |  |  |  |

## Clean install

```powershell
uv build
py -3.13 -m venv .verify-venv
.verify-venv\Scripts\pip install dist\stackshift-*.whl
.verify-venv\Scripts\stackshift --version
.verify-venv\Scripts\stackshift --help
```

Pass when the version and workflow command list print successfully.

## Offline smoke

Run `uv run pytest tests/test_core_smoke.py`. This exercises HashEmbedder, pairing, Procrustes, safe artifact save/load, adapter routing, live-state cutover state and metrics without network access.

## Safety checks

- Quantization: `uv run pytest tests/unit/test_coverage_paths.py -k quantized`
- Missing text: `uv run pytest tests/unit/test_coverage_paths.py -k missing`
- Leakage: `uv run pytest tests/property/test_invariants.py -k leakage`
- Artifact tamper: `uv run pytest tests/unit/test_coverage_paths.py -k tamper`
- State failure: `uv run pytest tests/unit/test_coverage_paths.py -k state_failure`

## Gate 1 reproduction

`uv run python benchmarks/gate1/run.py --seed 42` creates a manifest only. Install local models/datasets and implement the corpus command before recording results in `benchmarks/gate1/REPORT.md`. Do not infer an outcome from an unrun report.

## External integration tests

Qdrant/FAISS and provider tests require their dependencies, a reachable service or key, and are intentionally not evidence of success until executed. Use `pytest -m integration` after starting Qdrant and `pytest -m api` only with a non-production API key.
