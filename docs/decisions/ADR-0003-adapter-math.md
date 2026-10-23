# ADR-0003: Rectangular adapter math

## Status

Accepted.

## Decision

Map `d_new` inputs to `d_old` outputs. Procrustes uses economy SVD: tall matrices have orthonormal columns and wide matrices have orthonormal rows. Low-rank and residual adapters use a linear projection into the old space.

## Consequence

Every adapter output is normalized before cosine search, and all three dimensional relationships require numerical tests.
