"""Integration tests require a Qdrant service and are selected explicitly."""

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skip(reason="Qdrant Docker integration is implemented in Phase B")
def test_qdrant_contract_placeholder() -> None:
    pass
