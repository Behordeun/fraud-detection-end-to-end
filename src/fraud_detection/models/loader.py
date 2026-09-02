"""Format-detecting model loader.

Training now saves a Spark ``PipelineModel`` (assembler + classifier bundled)
so serving replays the exact stages the model was fit with. Older artifacts on
disk may still be a bare ``RandomForestClassificationModel``. Every consumer
loads through :func:`load_model` so both formats resolve the same way and no
call site hardcodes one class.
"""

import json
import os

from pyspark.ml import PipelineModel
from pyspark.ml.classification import RandomForestClassificationModel

_PIPELINE_CLASS = "org.apache.spark.ml.PipelineModel"
_RF_CLASS = "org.apache.spark.ml.classification.RandomForestClassificationModel"


def _read_model_class(model_path: str) -> str:
    """Read the persisted Spark ML class name from a saved model's metadata."""
    metadata_file = os.path.join(model_path, "metadata", "part-00000")
    if not os.path.isfile(metadata_file):
        raise FileNotFoundError(
            f"Model metadata not found at {metadata_file}; "
            f"{model_path} is not a saved Spark ML model."
        )
    with open(metadata_file, "r") as handle:
        return json.load(handle).get("class", "")


def load_model(model_path: str):
    """Load a saved Spark model, returning a PipelineModel or a bare classifier.

    The persisted metadata names the concrete class, so the correct loader is
    chosen without guessing. An unrecognized class raises rather than loading
    something the caller cannot ``transform`` as expected.
    """
    model_class = _read_model_class(model_path)
    if model_class == _PIPELINE_CLASS:
        return PipelineModel.load(model_path)
    if model_class == _RF_CLASS:
        return RandomForestClassificationModel.load(model_path)
    raise ValueError(f"Unsupported saved model class: {model_class!r}")
