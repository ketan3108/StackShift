import subprocess
import sys
from pathlib import Path


def test_claim_checker_passes_repository() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_claims.py"], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout


def test_claim_checker_rejects_planted_phrase(tmp_path: Path) -> None:
    checker = Path("scripts/check_claims.py").read_text(encoding="utf-8")
    assert "100x cost savings" in checker
