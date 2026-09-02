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
        apply_amount_scaler,
        drop_unnecessary_columns,
        fit_amount_scaler,
        handle_missing_values,
        load_data,
        save_preprocessed_data,
        set_features_and_target,
        split_data,
    )

    params = load_params()
    target = params["data"]["target_column"]
    processed_dir = str(PROJECT_ROOT / params["data"]["processed_dir"])

    data = load_data(str(PROJECT_ROOT / params["data"]["raw_file"]))
    data = drop_unnecessary_columns(data)
    data = handle_missing_values(data, target)

    # Split BEFORE scaling so the scaler is fit on training data only; fitting on
    # the full dataset would leak held-out statistics into the transformation.
    train_df, test_df, reserve_df = split_data(
        data,
        test_size=params["split"]["test_size"],
        reserve_size=params["split"]["reserve_size"],
        seed=params["split"]["seed"],
        target_column=target,
    )

    scaler_model, assembler = fit_amount_scaler(train_df)
    train_df = apply_amount_scaler(train_df, scaler_model, assembler)
    test_df = apply_amount_scaler(test_df, scaler_model, assembler)
    reserve_df = apply_amount_scaler(reserve_df, scaler_model, assembler)

    # Persist the fitted scaler so the serving path scales Amount with the same
    # training-distribution statistics instead of re-fitting per request.
    from fraud_detection.utils.config import AMOUNT_SCALER_DIR

    scaler_model.write().overwrite().save(str(AMOUNT_SCALER_DIR))

    # Assemble the model feature vector on each split. Reserve excludes the
    # target (dropped during the split), so only train/test carry it.
    train_df = set_features_and_target(train_df, target)
    test_df = set_features_and_target(test_df, target)

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
    model_dir = PROJECT_ROOT / params["paths"]["model_dir"]
    result = train_model(
        str(train_path),
        str(model_dir),
        n_trees=params["model"]["n_trees"],
        max_depth=params["model"]["max_depth"],
        seed=params["model"]["seed"],
    )

    # Persist the MLflow run id next to the model so the evaluate stage can
    # promote the exact logged model on its held-out AUC.
    run_id_file = model_dir.parent / "mlflow_run_id.txt"
    run_id_file.write_text(result["run_id"])


def evaluate() -> None:
    from fraud_detection.models.evaluate import evaluate_model
    from fraud_detection.models.registry import register_and_promote
    from fraud_detection.utils.config import (
        MLFLOW_REGISTERED_MODEL,
        MODEL_PROMOTION_MIN_AUC,
    )

    params = load_params()
    test_path = str(PROJECT_ROOT / params["data"]["engineered_dir"] / Path("test"))
    model_dir = PROJECT_ROOT / params["paths"]["model_dir"]
    metrics = evaluate_model(str(model_dir), test_path)

    metrics_file = PROJECT_ROOT / params["paths"]["metrics_file"]
    with open(metrics_file, "w") as handle:
        json.dump(metrics, handle, indent=2)
    print(f"Wrote metrics to {metrics_file}")

    # Gate registry promotion on the held-out test AUC, not the training AUC.
    run_id_file = model_dir.parent / "mlflow_run_id.txt"
    if run_id_file.exists():
        register_and_promote(
            model_uri=f"runs:/{run_id_file.read_text().strip()}/model",
            registered_model_name=MLFLOW_REGISTERED_MODEL,
            auc=metrics["auc"],
            min_auc=MODEL_PROMOTION_MIN_AUC,
        )


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
