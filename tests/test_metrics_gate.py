"""Tests for the CI metric gate.

The gate must fail closed: a model below the floor, an absent metrics file, a
missing metric, or malformed JSON all block the pipeline. Only a present metric
at or above the floor passes.
"""

import json

from scripts.check_metrics_gate import check_gate


def _write(tmp_path, payload):
    p = tmp_path / "metrics.json"
    p.write_text(json.dumps(payload))
    return str(p)


def test_passes_when_metric_meets_floor(tmp_path):
    path = _write(tmp_path, {"auc": 0.95})
    assert check_gate(path, "auc", 0.90) == 0


def test_passes_at_exact_floor(tmp_path):
    path = _write(tmp_path, {"auc": 0.90})
    assert check_gate(path, "auc", 0.90) == 0


def test_fails_below_floor(tmp_path):
    path = _write(tmp_path, {"auc": 0.80})
    assert check_gate(path, "auc", 0.90) == 1


def test_fails_when_file_missing(tmp_path):
    assert check_gate(str(tmp_path / "nope.json"), "auc", 0.90) == 1


def test_fails_when_metric_absent(tmp_path):
    path = _write(tmp_path, {"precision": 0.99})
    assert check_gate(path, "auc", 0.90) == 1


def test_fails_on_malformed_json(tmp_path):
    p = tmp_path / "metrics.json"
    p.write_text("{not valid json")
    assert check_gate(str(p), "auc", 0.90) == 1


def test_fails_on_nan_metric(tmp_path):
    # json.dump emits NaN by default; NaN < floor is False, so an undefined AUC
    # would slip through without the finite check.
    p = tmp_path / "metrics.json"
    p.write_text('{"auc": NaN}')
    assert check_gate(str(p), "auc", 0.90) == 1


def test_fails_on_non_numeric_metric(tmp_path):
    path = _write(tmp_path, {"auc": "high"})
    assert check_gate(path, "auc", 0.90) == 1
