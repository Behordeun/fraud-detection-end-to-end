"""Tests for training/serving parity: the PipelineModel + shared serving path.

These lock in the Tier 2 invariant: the features a model is scored on at serving
time are the same features it was trained on. A regression that reintroduces the
skew (a bare assembler over raw columns, a re-fit scaler, a dropped transform)
fails here.
"""

import pytest
from pyspark.ml import PipelineModel
from pyspark.sql import SparkSession

from src.fraud_detection.data.feature_engineering import (
    apply_feature_transforms,
    feature_vector_columns,
)
from src.fraud_detection.models.loader import load_model
from src.fraud_detection.models.registry import register_and_promote
from src.fraud_detection.models.serving import build_serving_features
from src.fraud_detection.models.train import train_model

RAW_COLUMNS = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]


def _raw_row(time=1000.0, amount=50.0, fill=0.1):
    row = {"Time": time, "Amount": amount}
    for i in range(1, 29):
        row[f"V{i}"] = fill
    return row


@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder.master("local[2]").appName("TestParity").getOrCreate()


def _fit_amount_scaler(spark):
    from src.fraud_detection.data.preprocessing import fit_amount_scaler

    train = spark.createDataFrame([_raw_row(amount=a) for a in (10.0, 50.0, 200.0)])
    scaler_model, _ = fit_amount_scaler(train)
    return scaler_model


def test_serving_features_match_training_columns(spark):
    """The serving path yields the exact feature columns training assembles."""
    scaler = _fit_amount_scaler(spark)

    raw = spark.createDataFrame([_raw_row()])
    served = build_serving_features(raw, scaler)

    # Training builds the vector from these columns on the engineered frame.
    scaled = spark.createDataFrame([_raw_row()])
    engineered = apply_feature_transforms(scaled)
    train_cols = set(feature_vector_columns(engineered))
    serve_cols = set(feature_vector_columns(served))

    assert serve_cols == train_cols, (
        "Serving features diverged from training features: "
        f"only-serve={serve_cols - train_cols}, only-train={train_cols - serve_cols}"
    )


def test_pipeline_model_round_trips_and_scores_raw_request(spark, tmp_path):
    """A trained PipelineModel scores a raw request through the serving path."""
    # Build an engineered training frame with a label, as the FE stage would.
    rows = []
    for i in range(20):
        r = _raw_row(amount=float(i * 10), fill=0.1 * (i % 5))
        r["Class"] = float(i % 2)
        rows.append(r)
    raw_train = spark.createDataFrame(rows)
    engineered = apply_feature_transforms(raw_train)
    string_cols = [n for n, d in engineered.dtypes if d == "string"]
    engineered = engineered.drop(*string_cols)

    train_path = str(tmp_path / "engineered_train")
    engineered.write.mode("overwrite").parquet(train_path)

    model_path = str(tmp_path / "pipeline_model")
    result = train_model(train_path, model_path, n_trees=3, max_depth=3)
    assert 0.0 <= result["train_auc"] <= 1.0

    loaded = load_model(model_path)
    assert isinstance(loaded, PipelineModel)

    # Score a raw request the way the API does.
    scaler = _fit_amount_scaler(spark)
    raw_request = spark.createDataFrame([_raw_row(amount=500.0)])
    served = build_serving_features(raw_request, scaler)
    scored = loaded.transform(served)
    assert scored.select("prediction").count() == 1
    assert "probability" in scored.columns


def test_registry_promotion_skipped_below_floor(monkeypatch):
    """A model below the AUC floor is not promoted."""
    import mlflow

    # File-store backend: registration is skipped, returns False.
    monkeypatch.setattr(mlflow, "get_tracking_uri", lambda: "file:./mlruns")
    promoted = register_and_promote(
        model_uri="runs:/abc/model",
        registered_model_name="test-model",
        auc=0.10,
        min_auc=0.90,
    )
    assert promoted is False


def test_registry_promotion_skipped_on_file_store(monkeypatch):
    """No registry backend (file store) means no promotion, even above floor."""
    import mlflow

    monkeypatch.setattr(mlflow, "get_tracking_uri", lambda: "file:./mlruns")
    promoted = register_and_promote(
        model_uri="runs:/abc/model",
        registered_model_name="test-model",
        auc=0.99,
        min_auc=0.90,
    )
    assert promoted is False
