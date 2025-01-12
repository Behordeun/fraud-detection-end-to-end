import yaml
from metadata.generated.schema.metadataIngestion.workflow import (
    OpenMetadataWorkflowConfig,
)
from metadata.ingestion.ometa.ometa_api import OpenMetadata


def load_config(config_path):
    """
    Load the OpenMetadata configuration from a YAML file.
    """
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config


def create_openmetadata_client(config_path):
    """
    Create an OpenMetadata client instance.
    """
    config = load_config(config_path)
    metadata_config = OpenMetadataWorkflowConfig.parse_obj(config)
    return OpenMetadata(metadata_config.workflowConfig.openMetadataServerConfig)


def ingest_metadata(client, metadata):
    """
    Ingest metadata for a specific entity.
    """
    client.ingest(metadata)
    print(f"Successfully ingested metadata: {metadata['name']}")


if __name__ == "__main__":
    CONFIG_PATH = "config.yaml"

    # Create the OpenMetadata client
    client = create_openmetadata_client(CONFIG_PATH)

    # Example: Ingest dataset metadata
    dataset_metadata = {
        "name": "fraud_detection_data",
        "description": "Dataset for fraud detection stored in MinIO",
        "owner": {"type": "user", "id": "admin"},
        "service": {"type": "s3", "id": "fraud-detection-minio"},
        "columns": [
            {"name": "id", "dataType": "INTEGER"},
            {"name": "amount", "dataType": "FLOAT"},
            {"name": "label", "dataType": "BOOLEAN"},
        ],
    }
    ingest_metadata(client, dataset_metadata)
