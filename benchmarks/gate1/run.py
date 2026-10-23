"""Gate 1 manifest writer; intentionally does not fabricate benchmark results."""

import argparse
import json
import platform
import subprocess
from datetime import UTC, datetime

p = argparse.ArgumentParser()
p.add_argument("--seed", type=int, default=42)
args = p.parse_args()
manifest = {
    "status": "NOT RUN",
    "seed": args.seed,
    "at": datetime.now(UTC).isoformat(),
    "platform": platform.platform(),
    "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
}
print(json.dumps(manifest, indent=2))
