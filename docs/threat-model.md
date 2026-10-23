# Threat model

| Threat | Mitigation |
| --- | --- |
| Tampered adapter artifact | safetensors and SHA-256 verification before load |
| Poisoned live state | schema validation, artifact hash checks, and audited writes |
| Leaked API key | environment/secrets-file input and log redaction |
| Malicious source text | treat corpus text as untrusted input; omit it from reports by default |
| Replica staleness | bounded TTL cache, last-known-good fallback, documented propagation |
