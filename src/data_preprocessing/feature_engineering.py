import logging

from pyspark.ml.feature import VectorAssembler
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, isnan, lit, log, sqrt, when

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FeatureEngineering")


def load_data(input_path: str) -> DataFrame:
    """
    Load the preprocessed data from Parquet files.
    """
    logger.info(f"Loading data from {input_path}...")
    spark = SparkSession.builder.appName(
        "CreditCardFraudFeatureEngineering"
    ).getOrCreate()

    try:
        df = spark.read.parquet(input_path)
        logger.info(f"Data loaded with schema: {df.schema}")
        return df
    except Exception as e:
        logger.error(f"Error loading data from {input_path}: {e}")
        raise


def handle_missing_values(df: DataFrame, threshold: float = 0.05) -> DataFrame:
    """
    Handle missing values in the dataset based on the percentage of missing observations.
    - Replace NaNs with the median if missing > threshold.
    - Drop rows if missing <= threshold.

    Args:
        df (DataFrame): Input DataFrame.
        threshold (float): Threshold for percentage of missing observations (default is 5%).

    Returns:
        DataFrame: DataFrame with missing values handled.
    """
    print("Handling missing values...")

    # Total number of rows in the dataset
    total_rows = df.count()

    for col_name in df.columns:
        # Calculate the percentage of missing values
        missing_count = df.filter(df[col_name].isNull() | isnan(df[col_name])).count()
        missing_percentage = missing_count / total_rows

        if missing_percentage > threshold:
            # Replace NaNs with the median
            print(
                f"Column '{col_name}' has {missing_percentage:.2%} missing values. Replacing with median."
            )
            median_value = (
                df.approxQuantile(col_name, [0.5], 0)[0]
                if col_name in [c[0] for c in df.dtypes if c[1] in ["double", "int"]]
                else None
            )
            if median_value is not None:
                df = df.withColumn(
                    col_name,
                    when(
                        df[col_name].isNull() | isnan(df[col_name]), lit(median_value)
                    ).otherwise(df[col_name]),
                )
        elif missing_percentage > 0:
            # Drop rows with NaNs if missing <= threshold
            print(
                f"Column '{col_name}' has {missing_percentage:.2%} missing values. Dropping rows."
            )
            df = df.filter(df[col_name].isNotNull())

    print("Missing values handled.")
    return df


def add_derived_features(df: DataFrame) -> DataFrame:
    """
    Add new derived features to the dataset.
    """
    logger.info("Adding derived features...")

    try:
        # Example: Log transformation (to reduce skewness for features > 0)
        numerical_cols = [
            field
            for field, dtype in df.dtypes
            if dtype in ["int", "double"] and field != "label"
        ]
        for col_name in numerical_cols:
            if col_name not in ["features", "scaled_features"]:
                df = df.withColumn(
                    f"log_{col_name}",
                    when(df[col_name] > 0, log(df[col_name])).otherwise(
                        lit(0)
                    ),  # Replace invalid values with 0
                )

        # Check if interaction columns exist
        if "feature1" in df.columns and "feature2" in df.columns:
            df = df.withColumn("interaction", col("feature1") * col("feature2"))
        else:
            logger.warning("Interaction columns ('feature1', 'feature2') not found.")

        # Add polynomial features and handle invalid values
        for col_name in numerical_cols:
            df = df.withColumn(
                f"{col_name}_squared",
                when(df[col_name].isNotNull(), pow(col(col_name), 2)).otherwise(lit(0)),
            )
            df = df.withColumn(
                f"{col_name}_sqrt",
                when(df[col_name] >= 0, sqrt(col(col_name))).otherwise(lit(0)),
            )

        logger.info("Derived features added successfully.")
        return df
    except Exception as e:
        logger.error(f"Error adding derived features: {e}")
        raise


def select_features(df: DataFrame, selected_columns: list) -> DataFrame:
    """
    Select the subset of features to keep for model training.
    """
    logger.info("Selecting features...")

    try:
        # Validate selected columns
        missing_columns = [col for col in selected_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns in dataset: {missing_columns}")

        # Use a VectorAssembler to create a feature vector
        assembler = VectorAssembler(
            inputCols=selected_columns, outputCol="engineered_features"
        )
        df = assembler.transform(df)
        logger.info(f"Selected features: {selected_columns}")
        return df
    except Exception as e:
        logger.error(f"Error selecting features: {e}")
        raise


def save_engineered_data(df: DataFrame, output_path: str):
    """
    Save the dataset with engineered features.
    """
    logger.info(f"Saving engineered data to {output_path}...")
    try:
        df.write.mode("overwrite").parquet(output_path)
        logger.info("Engineered data saved successfully.")
    except Exception as e:
        logger.error(f"Error saving engineered data to {output_path}: {e}")
        raise


if __name__ == "__main__":
    # Paths
    INPUT_PATH = "data/processed/train"  # Path to preprocessed training data
    OUTPUT_PATH = "data/processed/engineered"

    try:
        # Load preprocessed data
        data = load_data(INPUT_PATH)

        # Handle missing values
        data = handle_missing_values(data, threshold=0.05)

        # Add derived features
        data = add_derived_features(data)

        # Select features for training
        # Assuming we use all numerical columns and the new engineered features
        selected_features = [
            col
            for col in data.columns
            if "log_" in col or "_squared" in col or "_sqrt" in col
        ]
        data = select_features(data, selected_features)

        # Save engineered data
        save_engineered_data(data, OUTPUT_PATH)

    except Exception as e:
        logger.error(f"Feature engineering pipeline failed: {e}")
