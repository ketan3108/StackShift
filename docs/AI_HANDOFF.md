# StackShift continuation handoff

## Read this first

This is an AI-to-AI engineering handoff for `E:\StackShift`. Preserve the existing dirty working tree. Do not reset, checkout, or discard it. The current branch is `master` at committed revision `af13685`; there are uncommitted core-engine additions listed below. They are functional but are **not eligible to commit yet** because the repository coverage gate currently fails at 78.63% (required 90%). Do not lower quality gates or claim the build is final.

## Product objective

StackShift is a local-first Python CLI/SDK intended to measure behavior drift when replacing embedding models. It uses stored old-space vectors plus new-model embeddings of source text to train a new-to-old-space adapter. Workflow target: `scan -> train -> validate -> cutover -> rollback`, plus `ingest`, `report`, and later a local GUI. It must never promise safety, retrieval quality from neighbor overlap, eliminated rebuild work, or fabricated benchmark results.

## Immutable engineering/product rules

1. Pairing **never calls the old model**. It reads stored old vectors and embeds original text only with the new model.
2. Quantized/compressed vectors must abort. Missing source text must abort. Leakage across train/eval/candidate IDs must raise `LeakageError`.
3. Adapter mapping is new space -> old space and all output used for cosine search is L2-normalized.
4. Keep ARR, labeled retention, and synthetic proxy separate. Synthetic output is always explicitly a proxy.
5. Live state must eventually live in a production-reachable backend; local SQLite/files are not production truth.
6. Never invent Gate 1 results. Gate 1 remains a hard evidence stop before product/migration/UI work.
7. Keep 90% global coverage and >=95% for adapters, pairing, splits, and query state. Do not lower thresholds to pass.
8. Run ruff, mypy strict, pytest coverage, and claims checker before committing.

## Repository status

### Committed history

- `e20524c feat: initialize StackShift Phase 0 foundation`: packaging/tooling/docs/security scaffolding.
- `c337a4d feat: implement StackShift core workflow`: offline prototype.
- `af13685 fix: add Phase A threshold governance`: provisional threshold config, recommendation logic, audit, tests.

### Dirty working tree - preserve and finish

Modified: `pyproject.toml`, `uv.lock`, `src/stackshift/artifacts/store.py`, `tests/unit/test_coverage_paths.py`.

Untracked/in-progress: `benchmarks/`, `docs/TESTING.md`, Torch adapter files, Qdrant/FAISS connectors, local/OpenAI embedders, synthetic proxy, and unit tests for artifacts/synthetic/Torch.

### Latest actual verification

- `uv run --all-extras mypy src`: PASSED, 39 source files.
- `uv run --all-extras pytest --no-cov`: 22 passed, 1 skipped.
- `uv run --all-extras python scripts/check_claims.py`: PASSED.
- `uv build`: PASSED.
- `uv run --all-extras pytest`: FAILS only coverage: 78.63%, required 90%.

The coverage failure comes from untested external integration wrappers: FAISS 0%, Qdrant 0%, local embedder 0%, OpenAI embedder 0%. Add fake-client contract tests; do not omit them from coverage.

## File-by-file inventory

### Root/build/governance

- `pyproject.toml`: package metadata, runtime/dev extras, CLI entry point, Ruff/mypy/pytest/coverage config. In-progress extras include `local` and `all`; preserve compatibility and add `ui` only when UI exists.
- `uv.lock`: resolved dependency lock. Regenerate through `uv sync --all-extras` after manifest changes; do not hand edit.
- `Makefile`: targets `setup`, `lint`, `format`, `type`, `test`, `claims`, `build`. Windows host lacks make, so use equivalent `uv run` commands locally.
- `.gitignore`: Python caches, virtualenv, build products, secrets, local state.
- `.pre-commit-config.yaml`: Ruff and basic whitespace/YAML hooks.
- `README.md`: honest public status. Update only with evidence-backed features.
- `PROGRESS.md`: currently stale/incomplete; update after every phase with actual verification and NOT RUN entries.
- `CHANGELOG.md`: unreleased changes.
- `LICENSE`: intentional placeholder pending product licensing decision; no license granted.
- `NOTICE`, `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`: governance/security contribution policies.

### CI/GitHub

- `.github/workflows/ci.yml`: installs dependencies and runs Makefile quality targets.
- `.github/workflows/security.yml`: scheduled pip-audit.
- `.github/workflows/release.yml`: builds artifacts on version tags; does not publish.
- `.github/dependabot.yml`: weekly dependency/action updates.
- `.github/PULL_REQUEST_TEMPLATE.md`: review checklist template.

### Product docs

- `docs/architecture.md`: local artifact history vs remote production live-state design.
- `docs/audit-A.md`: Phase A deviations/corrections; update as deviations disappear.
- `docs/claims-contract.md`: approved/forbidden language.
- `docs/cli-reference.md`: currently incomplete because full commands/exit schemas are unfinished.
- `docs/data-handling.md`: local-first / provider-data boundaries.
- `docs/operations.md`: logs/audit expectations.
- `docs/roadmap.md`: v1 exclusions.
- `docs/runbook.md`: intended cutover/rollback process and TTL implications.
- `docs/security.md`: privacy and least-privilege policy.
- `docs/threat-model.md`: tampering, state poisoning, secrets, malicious text, staleness threats.
- `docs/TESTING.md` (uncommitted): manual test guide. Expand after Docker/Qdrant, state outage, GUI, and Gate 1 exist.
- `docs/decisions/ADR-0001-language-tooling.md`: Python/uv/Ruff/mypy choice.
- `docs/decisions/ADR-0002-live-state.md`: remote state design choice.
- `docs/decisions/ADR-0003-adapter-math.md`: rectangular adapter mapping decision.

### Configuration

- `config/thresholds.toml`: source of scan thresholds. Current status is `provisional`, provenance is pre-Gate-1, calibration is explicitly NOT CALIBRATED. Do not alter numeric values after benchmark observation without a documented calibration process.

### Package public surface

- `src/stackshift/__init__.py`: exposes `__version__`, `StackShiftSettings`, and `PreconditionError`; expand `__all__` deliberately with contract tests.
- `src/stackshift/__main__.py`: `python -m stackshift` entry point.
- `src/stackshift/py.typed`: PEP 561 typed-package marker.
- `src/stackshift/errors.py`: typed exception hierarchy. Add only actionable domain errors.
- `src/stackshift/config.py`: Pydantic `StackShiftSettings`: state TTL 5-30 sec, artifact/audit paths, raw-text report default false. Config layering is not implemented.
- `src/stackshift/logging.py`: Structlog setup and simple secret-field/OpenAI-key redaction. It needs recursive redaction/health events later.
- `src/stackshift/audit.py`: append-only local JSONL audit writer. It does not yet attach actor, git revision, state before/after, or every mutation.

### CLI

- `src/stackshift/cli/__init__.py`: package marker.
- `src/stackshift/cli/app.py`: Typer commands. `--version`, `scan`, `train`, `validate`, `cutover`, `rollback`, `ingest`, `report`. Only cutover/rollback perform basic local-file state operations. Scan/train/validate/ingest/report still respond “ready”; replace them with real pipeline invocation only after their core services exist. `--json` currently means simple JSON, not versioned schemas.

### Embedders

- `src/stackshift/embedders/__init__.py`: public re-exports only HashEmbedder/Protocol; update when real embedders become stable SDK API.
- `src/stackshift/embedders/base.py`: `EmbedderProtocol` and deterministic `HashEmbedder`; used by offline tests/demos.
- `src/stackshift/embedders/local.py` (uncommitted): `LocalEmbedder`, imports sentence-transformers lazily, caches individual `.npy` vectors using SHA-256(model_id + text), batches encoding, returns float32. Missing tests: mocked SentenceTransformer cache miss/hit, device forwarding, missing optional dependency, checkpoint/resume semantics.
- `src/stackshift/embedders/openai.py` (uncommitted): `OpenAIEmbedder`, requires `OPENAI_API_KEY`, lazy imports SDK, batches input, supports `dimensions`, bounded retries with exponential delay + jitter, returns float32. Missing: fake-client success/retry/exhaustion/dimensions tests, configured pricing/cost estimation, explicit timeout config, API-marked integration test.

### Connectors

- `src/stackshift/connectors/__init__.py`: re-exports only in-memory contract/classes; expand cautiously.
- `src/stackshift/connectors/base.py`: `VectorStoreProtocol`, plus `InMemoryVectorStore` for tests. Its `sample` deterministic sorting is a basic test implementation, not stratification.
- `src/stackshift/connectors/faiss.py` (uncommitted): `FaissVectorStore`, wraps an FAISS-like index plus `ids` and mandatory `doc_id_to_text`. Rejects type names containing `pq`, `sq`, `binary`; reconstructs vectors by index position and searches. Missing: fake FAISS regular/PQ/SQ tests, ID mapping validation, pagination/large-index behavior.
- `src/stackshift/connectors/qdrant.py` (uncommitted): `QdrantVectorStore`, lazy qdrant-client import, collection quantization check, scroll/sample, retrieve vectors/text payload, query search. Missing: fake Qdrant contract tests, retry/pagination/stratified sampling, Docker test, clear IDs/count error for quantized/missing text.

### Pairing/splits

- `src/stackshift/splits.py`: deterministic split and pairwise disjointness. `LeakageError` on overlap. Coverage meets target.
- `src/stackshift/pairing.py`: `PairingBuilder` reads stored vectors, rejects store-reported quantization, fetches text, new-embeds only, normalizes, splits, checks eval/candidate isolation, outputs `PairingResult`. It does not include error IDs/counts, stratification, checkpoints, or old-model-reachability warning. Coverage meets target.

### Adapters

- `src/stackshift/adapters/__init__.py`: exports protocol/normalizer/Procrustes only.
- `src/stackshift/adapters/base.py`: L2 row-normalization and AdapterProtocol.
- `src/stackshift/adapters/procrustes.py`: closed-form SVD rectangular mapping. Square/tall/wide correctness/property tests exist and coverage is 100%.
- `src/stackshift/adapters/lowrank_affine.py`: old NumPy least-squares baseline. Do not represent as the final trained LA path once Torch model becomes public.
- `src/stackshift/adapters/residual_mlp.py`: old NumPy Procrustes-projection baseline. Same rule.
- `src/stackshift/adapters/torch_training.py` (uncommitted): seed utility, generic AdamW deterministic training utility (50 epochs default, patience 5, 80/20 split), `TrainingStats`, and `TorchResidual` with projection/256 GELU/dropout 0.1. It needs a public wrapper that transforms NumPy inputs and L2-normalizes output.
- `src/stackshift/adapters/torch_lowrank.py` (uncommitted): Torch `U(Vx)+bias` rectangular low-rank architecture. It needs a public wrapper and trained artifact serialization.
- `src/stackshift/adapters/factory.py` (uncommitted): `train_all` currently fits Procrustes and trains Torch residual/low-rank. It returns models and stats. It needs normalized public adapter wrappers, validation metrics, CPU/GPU selection, and tests for non-linear warp vs OP.

### Artifacts

- `src/stackshift/artifacts/store.py` (modified/uncommitted): migrated `save_artifact` to `safetensors.numpy.save_file`, writes JSON manifest and SHA-256, verifies safe artifact digest/dimensions on load, handles legacy `.npy` with DeprecationWarning. It needs complete manifest fields (training stats, model versions, library versions, normalization), model compatibility validation, artifact registry integration, and a safe migration writer. Tests for tamper and legacy load exist uncommitted.

### Evaluation

- `src/stackshift/eval/__init__.py`: marker only.
- `src/stackshift/eval/metrics.py`: neighbor overlap, recall@k, nDCG@k, retention. nDCG needs validation against pytrec_eval/ranx in Phase D.
- `src/stackshift/eval/neighbor_overlap.py`: average neighbor recovery/ARR calculation.
- `src/stackshift/eval/labeled.py`: labeled retention dictionary against direct new-model reference.
- `src/stackshift/eval/synthetic.py` (uncommitted): only `synthetic_proxy_notice`; full controlled LLM query generation is not implemented.
- Missing required `eval/beir_harness.py`: must fetch/run SciFact, NFCorpus, FiQA, enforce isolation, create old/new reference paths, calculate direct-vs-adapter retention.

### Scan

- `src/stackshift/scan/thresholds.py`: TOML loader into typed ThresholdConfig.
- `src/stackshift/scan/recommend.py`: threshold + labeled-retention + drastic-drift recommendation with reasons/provenance.
- `src/stackshift/scan/pipeline.py`: only evaluates supplied lists and returns typed ScanResult. Missing real corpus pipeline, train-all call, candidates, reports, costs, repeatability, worst-affected queries.
- `src/stackshift/scan/__init__.py`: marker.

### Query state/routing

- `src/stackshift/query/state.py`: `LiveState`, StateBackend protocol, atomic local FileStateBackend, CachedStateReader. TTL 5-30 secs and last-known-good fallback are implemented. Missing remote Qdrant/object/env backends, CAS, health/degradation observability, schema/hash validation.
- `src/stackshift/query/router.py`: synchronously embeds query and applies adapter in adapter mode. Missing thread safety, async path, artifact/version validation, health metric.
- `src/stackshift/query/__init__.py`: marker.

### Tests

- `tests/test_foundations.py`: version/help/CLI, config range, redaction, audit basics.
- `tests/test_claims.py`: claims checker baseline.
- `tests/test_core_smoke.py`: HashEmbedder -> memory store -> pairing -> baseline adapters -> artifact -> state/router -> metrics/scan. Update to assert safetensors rather than assumptions about `.npy`.
- `tests/unit/test_coverage_paths.py` (modified): error branches for pairing, artifacts/state, adapters, CLI. Update to safetensors names (partially updated) and do not leave duplicate/stale assertions.
- `tests/unit/test_artifacts.py` (uncommitted): safetensors tamper and legacy migration tests.
- `tests/unit/test_synthetic.py` (uncommitted): proxy label test.
- `tests/unit/test_torch_training.py` (uncommitted): residual and low-rank deterministic rectangular training smoke test. Add equal-seed weights and nonlinear-warp comparison tests.
- `tests/property/test_invariants.py`: Hypothesis normalization, square/tall/wide Procrustes tests, leakage, threshold behavior.
- `tests/integration/test_qdrant_contract.py`: skipped placeholder. Replace with Docker service integration test after fake contract suite exists.
- `tests/e2e/`: directory only; no e2e tests.

### Benchmarks

- `benchmarks/gate1/run.py` (uncommitted): outputs a NOT RUN manifest with seed/platform/commit; it does not run models/datasets.
- `benchmarks/gate1/REPORT.md` (uncommitted): explicitly says NOT RUN and records basic reproduction instructions. Do not fill metrics until commands run.
- `benchmarks/latency/` and `benchmarks/results/`: directories do not currently exist or have no committed meaningful result. Add real scripts/manifests only.

### Scripts

- `scripts/check_claims.py`: scans README/docs/src text for forbidden phrases. It does not scan all future UI/frontend paths yet; extend roots when they are added.

## Exact next execution order

1. **Do not commit current work yet.** First make `uv run --all-extras pytest` meet 90% overall coverage.
2. Add fake Qdrant client tests: construct fake collection config, scroll/retrieve/query responses; test normal and quantized behavior.
3. Add fake FAISS index tests: reconstruct/search normal, fake PQ class rejection, missing text callable behavior.
4. Add fake sentence-transformers module test via monkeypatch/sys.modules: model call, cache miss then cache hit, float32.
5. Add fake OpenAI module/client tests: no-key error, successful dimensions request, temporary failure/retry via monkeypatch sleep, exhausted retry.
6. Extend Torch tests: deterministic equal seed state_dict, output L2 wrapper (implement wrapper), nonlinear synthetic warp quality comparison to Procrustes, early stopping stats.
7. Finish safetensors manifest schema: stats, library versions, model version compatibility; migration test that writes the new format.
8. Run `ruff`, `mypy`, `pytest`, `check_claims`, `uv build`; only commit if all pass.
9. Then implement BEIR harness, benchmark/latency scripts, and Gate 1. At Gate 1, run actual benchmarks or record NOT RUN. Do not start full scan/migration/UI without outcome.

## Commands

```powershell
uv sync --all-extras
uv run --all-extras ruff check src tests benchmarks
uv run --all-extras mypy src
uv run --all-extras pytest
uv run --all-extras python scripts/check_claims.py
uv build
```

Windows has no `make` on this host; use the commands above. Do not add a fake passing Make target.

## What must not be claimed

Do not claim full build, enterprise readiness, Qdrant support, API support, BEIR performance, zero downtime, benchmark success, or Gate 1 pass. Only offline/fake-client functionality has evidence so far. The CLI’s “ready” actions are not full workflows.