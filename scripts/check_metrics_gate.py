"""Fail CI when a trained model's held-out metric is below its floor.

The pipeline's evaluate stage writes metrics.json from the held-out test set.
This gate reads that file and exits non-zero when the primary metric is below a
configured threshold, so a regression cannot merge or be published even though
`dvc repro` itself succeeded. Deterministic and dependency-free, so it runs as a
plain CI step rather than through the model.
"""

import argparse
import json
import sys
from pathlib import Path


def check_gate(metrics_path: str, metric: str, minimum: float) -> int:
    """Return 0 if metrics[metric] >= minimum, else 1. Missing file/key is a fail.

    A missing metrics file or metric key is treated as a gate failure, not a
    pass: the gate must never let an unmeasured model through.
    """
    path = Path(metrics_path)
    if not path.is_file():
        print(f"GATE FAIL: metrics file not found at {metrics_path}", file=sys.stderr)
        return 1

    try:
        metrics = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(f"GATE FAIL: metrics file is not valid JSON: {exc}", file=sys.stderr)
        return 1

    if metric not in metrics:
        print(
            f"GATE FAIL: metric {metric!r} not in metrics file "
            f"(have: {sorted(metrics)})",
            file=sys.stderr,
        )
        return 1

    value = metrics[metric]
    if value < minimum:
        print(
            f"GATE FAIL: {metric}={value:.4f} is below the floor {minimum:.4f}",
            file=sys.stderr,
        )
        return 1

    print(f"GATE PASS: {metric}={value:.4f} >= {minimum:.4f}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Gate CI on a model metric floor.")
    parser.add_argument("--metrics", default="metrics.json")
    parser.add_argument("--metric", default="auc")
    parser.add_argument("--min", type=float, required=True, dest="minimum")
    args = parser.parse_args()
    return check_gate(args.metrics, args.metric, args.minimum)


if __name__ == "__main__":
    sys.exit(main())
