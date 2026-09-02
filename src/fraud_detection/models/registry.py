"""MLflow Model Registry promotion, gated on a metric floor.

Registering a model version and moving it to a serving stage is what turns "a
model was trained" into "this specific model is the one to serve". Promotion is
gated: a new version advances to the target stage only when its AUC clears
``MODEL_PROMOTION_MIN_AUC``, so a regression cannot silently become the served
model.

The registry needs a database-backed tracking server. On a local file store
(the CI default, ``file:./mlruns``) the registry API is unavailable, so these
helpers detect that and skip registration with a clear message rather than
failing the training run.
"""

import logging

import mlflow

logger = logging.getLogger(__name__)


def _registry_available() -> bool:
    """True when the tracking backend supports the Model Registry.

    The file store cannot serve the registry API. Any non-file scheme
    (``http``, ``https``, ``databricks``, a DB URI) is assumed to support it.
    """
    uri = mlflow.get_tracking_uri()
    return not uri.startswith("file:") and not uri.startswith("/")


def register_and_promote(
    model_uri: str,
    registered_model_name: str,
    auc: float,
    min_auc: float,
    stage: str = "Production",
) -> bool:
    """Register ``model_uri`` and promote it to ``stage`` iff ``auc >= min_auc``.

    Returns True when a version was promoted, False when promotion was skipped
    (metric below floor, or no registry backend). Never raises on a missing
    registry: training must still succeed on the file-store CI backend.
    """
    if auc < min_auc:
        logger.warning(
            "Model AUC %.4f is below the promotion floor %.4f; "
            "registering without promotion.",
            auc,
            min_auc,
        )

    if not _registry_available():
        logger.info(
            "Tracking backend %s has no Model Registry; skipping registration. "
            "Point MLFLOW_TRACKING_URI at a tracking server to enable it.",
            mlflow.get_tracking_uri(),
        )
        return False

    client = mlflow.tracking.MlflowClient()
    try:
        client.create_registered_model(registered_model_name)
    except mlflow.exceptions.MlflowException as exc:
        # RESOURCE_ALREADY_EXISTS is the normal steady state after the first
        # run; any other registry error (auth, network, corrupt state) is real
        # and must not be masked.
        if getattr(exc, "error_code", "") != "RESOURCE_ALREADY_EXISTS":
            raise

    version = mlflow.register_model(model_uri, registered_model_name)

    if auc < min_auc:
        return False

    client.transition_model_version_stage(
        name=registered_model_name,
        version=version.version,
        stage=stage,
        archive_existing_versions=True,
    )
    logger.info(
        "Promoted %s version %s to %s (AUC %.4f >= %.4f).",
        registered_model_name,
        version.version,
        stage,
        auc,
        min_auc,
    )
    return True
