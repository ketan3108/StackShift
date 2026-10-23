# Architecture

StackShift is a CLI and Python SDK. The planned core maps new-model query vectors into an existing old-vector space, then evaluates behavior before a cutover. Local SQLite will track artifact history, while production live state will be stored remotely so all SDK replicas can observe it.

The v1 supported live-state preference is Qdrant metadata, then an object-store JSON document, then environment/config service state. The SDK cache will default to 15 seconds and be configurable from 5 through 30 seconds. A rollback config swap is fast, but replica propagation is bounded by that cache TTL.
