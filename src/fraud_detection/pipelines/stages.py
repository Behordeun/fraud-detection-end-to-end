"""DVC pipeline stage runners.

Each function is a thin entry point for one `dvc.yaml` stage. It reads
`params.yaml`, calls the existing data/model functions, and (for the evaluate
stage) writes a DVC-tracked metrics file. Keeping the orchestration here leaves
the underlying data and model modules unchanged and gives DVC a single,
parametrized command per stage.
"""

import argparse
import json
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PARAMS_FILE = PROJECT_ROOT / "params.yaml"


def load_params() -> dict:
    with open(PARAMS_FILE, "r") as handle:
        return yaml.safe_load(handle)


def preprocess() -> None:
    from fraud_detection.data.preprocessing import (
        drop_unnecessary_columns,
        handle_missing_values,
        load_data,
        save_preprocessed_data,
        scale_features,
        set_features_and_target,
        split_data,
    )

    params = load_params()
    target = params["data"]["target_column"]
    processed_dir = str(PROJECT_ROOT / params["data"]["processed_dir"])

    data = load_data(str(PROJECT_ROOT / params["data"]["raw_file"]))
    data = drop_unnecessary_columns(data)
    data = handle_missing_values(data, target)
    data = scale_features(data)
    if target not in data.columns:
        raise ValueError(f"Target column '{target}' missing from processed dataset")
    data = set_features_and_target(data, target)

    train_df, test_df, reserve_df = split_data(
        data,
        test_size=params["split"]["test_size"],
        reserve_size=params["split"]["reserve_size"],
        seed=params["split"]["seed"],
    )
    save_preprocessed_data(train_df, test_df, reserve_df, processed_dir)


def feature_engineering() -> None:
    from fraud_detection.data.feature_engineering import engineer_features

    params = load_params()
    engineer_features(
        str(PROJECT_ROOT / params["data"]["processed_dir"]),
        str(PROJECT_ROOT / params["data"]["engineered_dir"]),
    )


def train() -> None:
    from fraud_detection.models.train import train_model

    params = load_params()
    train_path = str(PROJECT_ROOT / params["data"]["engineered_dir"] / Path("train"))
    train_model(
        train_path,
        str(PROJECT_ROOT / params["paths"]["model_dir"]),
        n_trees=params["model"]["n_trees"],
        max_depth=params["model"]["max_depth"],
        seed=params["model"]["seed"],
    )


def evaluate() -> None:
    from fraud_detection.models.evaluate import evaluate_model

    params = load_params()
    test_path = str(PROJECT_ROOT / params["data"]["engineered_dir"] / Path("test"))
    metrics = evaluate_model(
        str(PROJECT_ROOT / params["paths"]["model_dir"]),
        test_path,
    )

    metrics_file = PROJECT_ROOT / params["paths"]["metrics_file"]
    with open(metrics_file, "w") as handle:
        json.dump(metrics, handle, indent=2)
    print(f"Wrote metrics to {metrics_file}")


STAGES = {
    "preprocess": preprocess,
    "feature_engineering": feature_engineering,
    "train": train,
    "evaluate": evaluate,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a DVC pipeline stage.")
    parser.add_argument("stage", choices=sorted(STAGES))
    args = parser.parse_args()
    STAGES[args.stage]()


if __name__ == "__main__":
    main()
