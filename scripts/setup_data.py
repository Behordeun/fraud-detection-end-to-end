#!/usr/bin/env python3
"""Acquire the credit-card fraud dataset for the pipeline.

Resolution order:
1. A real dataset already at data/raw/creditcard_2023.csv is used as-is.
2. If the Kaggle CLI and credentials are present, download the real dataset.
3. Otherwise generate a deterministic synthetic dataset with the same schema,
   so the pipeline is runnable without Kaggle access.

The full Kaggle dataset is large and license-restricted, so it is never
committed; DVC tracks it (see dvc.yaml). A small committed sample for CI is
produced with `--sample`.
"""

import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATASET_PATH = RAW_DIR / "creditcard_2023.csv"
SAMPLE_PATH = RAW_DIR / "creditcard_sample.csv"
KAGGLE_DATASET = "nelgiriyewithana/credit-card-fraud-detection-dataset-2023"

FEATURE_COLUMNS = [f"V{i}" for i in range(1, 29)]


def generate_synthetic(n_samples: int, seed: int = 42) -> pd.DataFrame:
    """Build a synthetic dataset matching the real schema (Time, V1-V28, Amount, Class)."""
    rng = np.random.default_rng(seed)
    frame = {f"V{i}": rng.normal(0, 1, n_samples) for i in range(1, 29)}
    frame["Time"] = rng.uniform(0, 172800, n_samples)
    frame["Amount"] = rng.lognormal(3, 1.5, n_samples)

    labels = np.zeros(n_samples)
    n_fraud = max(1, int(n_samples * 0.02))
    fraud_idx = rng.choice(n_samples, n_fraud, replace=False)
    labels[fraud_idx] = 1
    # Push fraud rows off the normal distribution so the target is learnable.
    for col in ("V1", "V2", "V3", "V4", "V14"):
        frame[col][fraud_idx] *= rng.uniform(2, 5, n_fraud)
    frame["Amount"][fraud_idx] *= rng.uniform(0.1, 3, n_fraud)
    frame["Class"] = labels

    ordered = ["Time"] + FEATURE_COLUMNS + ["Amount", "Class"]
    return pd.DataFrame(frame)[ordered]


def try_kaggle_download() -> bool:
    """Download the real dataset via the Kaggle CLI. Returns True on success."""
    try:
        subprocess.run(
            [
                "kaggle",
                "datasets",
                "download",
                "-d",
                KAGGLE_DATASET,
                "-p",
                str(RAW_DIR),
                "--unzip",
            ],
            check=True,
        )
        return DATASET_PATH.exists()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"Kaggle download unavailable ({exc}); falling back to synthetic data.")
        return False


def summarize(path: Path) -> None:
    frame = pd.read_csv(path)
    print(f"Dataset at {path}")
    print(f"  shape: {frame.shape}")
    print(f"  fraud rate: {frame['Class'].mean():.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Write a small committed CI sample to creditcard_sample.csv.",
    )
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=2000,
        help="Rows for the CI sample (default 2000).",
    )
    parser.add_argument(
        "--synthetic-rows",
        type=int,
        default=10000,
        help="Rows for the synthetic full dataset (default 10000).",
    )
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if args.sample:
        generate_synthetic(args.sample_rows).to_csv(SAMPLE_PATH, index=False)
        summarize(SAMPLE_PATH)
        return

    if DATASET_PATH.exists():
        print("Real dataset already present.")
        summarize(DATASET_PATH)
        return

    if try_kaggle_download():
        summarize(DATASET_PATH)
        return

    generate_synthetic(args.synthetic_rows).to_csv(DATASET_PATH, index=False)
    summarize(DATASET_PATH)


if __name__ == "__main__":
    sys.exit(main())
