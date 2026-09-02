"""Real API tests for the fraud-detection service.

The API loads a PipelineModel and the fitted Amount scaler at startup and scores
a raw transaction through the shared serving path. These tests inject a small
real model + scaler, then exercise /health and /predict through FastAPI's test
client, so a broken serving path (the training/serving skew this tier fixes)
surfaces as a failing request rather than a silently wrong score.
"""

import pytest
from fastapi.testclient import TestClient
from pyspark.sql import SparkSession

from src.fraud_detection.data.feature_engineering import apply_feature_transforms
from src.fraud_detection.models.train import train_model


def _raw_row(time=1000.0, amount=50.0, fill=0.1, label=None):
    row = {"Time": time, "Amount": amount}
    for i in range(1, 29):
        row[f"V{i}"] = fill
    if label is not None:
        row["Class"] = label
    return row


@pytest.fixture(scope="module")
def spark():
    return SparkSession.builder.master("local[2]").appName("TestAPI").getOrCreate()


@pytest.fixture(scope="module")
def api_client(spark, tmp_path_factory):
    """Train a small model + scaler, point the app at them, yield a TestClient."""
    tmp = tmp_path_factory.mktemp("api_artifacts")

    # Train a PipelineModel on a small engineered frame.
    rows = [
        _raw_row(amount=float(i * 10), fill=0.1 * (i % 5), label=float(i % 2))
        for i in range(20)
    ]
    engineered = apply_feature_transforms(spark.createDataFrame(rows))
    string_cols = [n for n, d in engineered.dtypes if d == "string"]
    engineered = engineered.drop(*string_cols)
    train_path = str(tmp / "engineered_train")
    engineered.write.mode("overwrite").parquet(train_path)

    model_path = str(tmp / "pipeline_model")
    train_model(train_path, model_path, n_trees=3, max_depth=3)

    # Fit + persist an Amount scaler as preprocess would.
    from src.fraud_detection.data.preprocessing import fit_amount_scaler

    scaler_train = spark.createDataFrame(
        [_raw_row(amount=a) for a in (10.0, 50.0, 200.0)]
    )
    scaler_model, _ = fit_amount_scaler(scaler_train)
    scaler_path = str(tmp / "amount_scaler")
    scaler_model.write().overwrite().save(scaler_path)

    from src.fraud_detection.api import app as app_module
    from src.fraud_detection.models.loader import load_model
    from src.fraud_detection.models.serving import load_amount_scaler

    app_module.model = load_model(model_path)
    app_module.amount_scaler = load_amount_scaler(scaler_path)

    return TestClient(app_module.app)


def test_health_reports_loaded(api_client):
    resp = api_client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
    assert body["model_loaded"] is True


def test_predict_returns_wellformed_response(api_client):
    resp = api_client.post("/predict", json=_raw_row(amount=500.0))
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert isinstance(body["is_fraud"], bool)
    assert 0.0 <= body["fraud_probability"] <= 1.0
    assert body["confidence"] in {"low", "medium", "high"}


def test_predict_503_when_model_unloaded(spark):
    """With no model loaded, /predict reports the service is not ready."""
    from src.fraud_detection.api import app as app_module

    saved_model, saved_scaler = app_module.model, app_module.amount_scaler
    app_module.model = None
    app_module.amount_scaler = None
    try:
        client = TestClient(app_module.app)
        resp = client.post("/predict", json=_raw_row())
        assert resp.status_code == 503
    finally:
        app_module.model, app_module.amount_scaler = saved_model, saved_scaler
