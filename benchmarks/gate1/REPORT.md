# Gate 1 report

Status: NOT RUN.

No benchmark result is recorded because this host has not run the required BEIR datasets, 100K-document model pass, Qdrant service, or optional OpenAI API test.

## Reproduction

1. Install `uv sync --all-extras`.
2. Set `OPENAI_API_KEY` only for the API pair.
3. Run `uv run python benchmarks/gate1/run.py --seed 42`.
4. Record command, commit hash, CPU/GPU, datasets, runtime, and all metric values here.

The pre-registered Gate 1 thresholds remain unchanged. A human must determine the outcome after results exist.
