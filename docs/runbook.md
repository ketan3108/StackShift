# Runbook

The production cutover procedure will verify the adapter hash, dimensions, and model IDs before atomically updating remote live state. The SDK will use its last known good state if the state backend is unavailable. Rollback is a remote configuration swap; rollout across replicas is bounded by the documented cache TTL.
