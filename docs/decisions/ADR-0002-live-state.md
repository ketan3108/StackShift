# ADR-0002: Remote live state

## Status

Accepted.

## Decision

Keep artifact history locally but locate live routing state in a production-reachable backend. Prefer Qdrant metadata, with object storage and environment/config-service variants planned behind one interface.

## Consequence

An operation's config swap and replica propagation are separate; the latter is bounded by the state cache TTL.
