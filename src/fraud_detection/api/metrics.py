"""Prometheus metrics for the fraud-detection API.

Defines the collectors once so the app and its tests share the same registry.
The API exposes these at /metrics for a Prometheus scrape; a Grafana dashboard
reads them to show request rate, latency, prediction mix, and whether the model
is loaded.
"""

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram
from prometheus_client import generate_latest as _generate_latest

PREDICTION_REQUESTS = Counter(
    "fraud_prediction_requests_total",
    "Total /predict requests by outcome.",
    ["outcome"],  # fraud, legit, error
)

PREDICTION_LATENCY = Histogram(
    "fraud_prediction_latency_seconds",
    "Latency of a /predict call in seconds.",
)

MODEL_LOADED = Gauge(
    "fraud_model_loaded",
    "1 when the model and scaler are loaded and the API can serve, else 0.",
)


def render_metrics():
    """Return (body, content_type) for the /metrics endpoint."""
    return _generate_latest(), CONTENT_TYPE_LATEST
