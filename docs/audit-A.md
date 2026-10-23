# Phase A audit - corrective refactor

Date: 2026-10-23

## Audit result

The initial prototype passed its limited offline suite but did not meet the full master specification.

## Corrected in Phase A

- Scan recommendation no longer hard-codes a threshold. It loads versioned thresholds from `config/thresholds.toml` and emits status, provenance, and calibration evidence.
- Thresholds are explicitly `provisional` and identify that Gate 1 calibration has not run.
- Recommendations consider ARR, labeled nDCG@10 retention when supplied, and a drastic-drift floor.
- Scan results are typed and retain metric mode separately from labeled retention.
- Property/invariant tests and the required test-directory structure were added.

## Still outstanding after Phase A

- Sentence-transformers/OpenAI embedders, Qdrant/FAISS connectors, remote state backends.
- PyTorch trained low-rank/residual adapters and safetensors migration.
- BEIR/Gate 1 benchmark harness and results.
- Full corpus CLI workflows, Docker demo, SQLite registry, GUI, enterprise hardening, docs site and release work.

## Notes

No external benchmark result has been claimed. Existing artifact storage is `.npy` without pickle; it remains a deviation until Phase C safetensors migration.
