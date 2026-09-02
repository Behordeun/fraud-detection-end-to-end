"""Tests for drift-triggered retraining signalling.

The drift report must flag retrain_recommended when the share of drifted
features crosses the configured threshold. This also guards the module import:
it previously imported a nonexistent sklearn symbol, so it could never run.
"""

import numpy as np
import pandas as pd

from src.fraud_detection.monitoring import advanced_drift_detection as add


def _make_detector(tmp_path, reference):
    ref_path = tmp_path / "reference"
    reference.to_parquet(ref_path)
    return add.AdvancedDriftDetector(reference_data_path=str(ref_path))


def test_no_retrain_when_distribution_is_stable(tmp_path, monkeypatch):
    monkeypatch.setattr(add, "DRIFT_RETRAIN_PCT", 30.0)
    rng = np.random.default_rng(0)
    ref = pd.DataFrame({"V1": rng.normal(0, 1, 500), "V2": rng.normal(0, 1, 500)})
    detector = _make_detector(tmp_path, ref)

    # New data drawn from the same distribution: little to no drift.
    new = pd.DataFrame({"V1": rng.normal(0, 1, 500), "V2": rng.normal(0, 1, 500)})
    new_path = tmp_path / "new"
    new.to_parquet(new_path)

    report = detector.generate_drift_report(
        str(new_path), output_path=str(tmp_path / "report.json")
    )
    assert report["retrain_recommended"] is False
    assert report["retrain_threshold_pct"] == 30.0


def test_retrain_recommended_when_distribution_shifts(tmp_path, monkeypatch):
    monkeypatch.setattr(add, "DRIFT_RETRAIN_PCT", 30.0)
    rng = np.random.default_rng(1)
    ref = pd.DataFrame({"V1": rng.normal(0, 1, 500), "V2": rng.normal(0, 1, 500)})
    detector = _make_detector(tmp_path, ref)

    # New data heavily shifted on both features: drift on the majority.
    new = pd.DataFrame({"V1": rng.normal(8, 1, 500), "V2": rng.normal(8, 1, 500)})
    new_path = tmp_path / "new"
    new.to_parquet(new_path)

    report = detector.generate_drift_report(
        str(new_path), output_path=str(tmp_path / "report.json")
    )
    assert report["retrain_recommended"] is True
