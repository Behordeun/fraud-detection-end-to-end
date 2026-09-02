"""Real API tests for the fraud-detection service.

The API loads a PipelineModel and the fitted Amount scaler at startup and scores
a raw transaction through the shared serving path. These tests train a small
real model + scaler, point the app module at them, and call the endpoint
coroutines directly. Calling the handlers (rather than driving an HTTP client)
keeps the test independent of the installed starlette/httpx TestClient version
while still exercising the real request model and serving path, so the
training/serving skew this tier fixes surfaces as a failing prediction.
"""

import asyncio

import pytest
from fastapi import HTTPException
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
def app_module(spark, tmp_path_factory):
    """Train a small model + scaler and point the app module's globals at them."""
    tmp = tmp_path_factory.mktemp("api_artifacts")

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
    return app_module


def test_health_reports_loaded(app_module):
    body = asyncio.run(app_module.health_check())
    assert body["status"] == "healthy"
    assert body["model_loaded"] is True


def test_predict_returns_wellformed_response(app_module):
    transaction = app_module.TransactionData(**_raw_row(amount=500.0))
    response = asyncio.run(app_module.predict_fraud(transaction))
    assert isinstance(response.is_fraud, bool)
    assert 0.0 <= response.fraud_probability <= 1.0
    assert response.confidence in {"low", "medium", "high"}


def test_predict_503_when_model_unloaded(app_module):
    """With no model loaded, /predict reports the service is not ready."""
    saved_model, saved_scaler = app_module.model, app_module.amount_scaler
    app_module.model = None
    app_module.amount_scaler = None
    try:
        transaction = app_module.TransactionData(**_raw_row())
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(app_module.predict_fraud(transaction))
        assert exc_info.value.status_code == 503
    finally:
        app_module.model, app_module.amount_scaler = saved_model, saved_scaler


def test_metrics_endpoint_exposes_prometheus_text(app_module):
    """The /metrics endpoint returns Prometheus text including our collectors."""
    resp = asyncio.run(app_module.metrics())
    body = resp.body.decode() if hasattr(resp.body, "decode") else str(resp.body)
    assert "fraud_prediction_requests_total" in body
    assert "fraud_model_loaded" in body


def test_predict_increments_prediction_counter(app_module):
    """A successful prediction increments the outcome counter."""
    from fraud_detection.api.metrics import PREDICTION_REQUESTS

    before = sum(
        s.value
        for m in PREDICTION_REQUESTS.collect()
        for s in m.samples
        if s.name.endswith("_total")
    )
    transaction = app_module.TransactionData(**_raw_row(amount=500.0))
    asyncio.run(app_module.predict_fraud(transaction))
    after = sum(
        s.value
        for m in PREDICTION_REQUESTS.collect()
        for s in m.samples
        if s.name.endswith("_total")
    )
    assert after > before
