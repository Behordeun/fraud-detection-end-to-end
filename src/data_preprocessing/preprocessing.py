from pyspark.ml.feature import StandardScaler, VectorAssembler
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import lit, when


def load_data(file_path: str) -> DataFrame:
    """
    Load the dataset from a CSV file.
    """
    spark = SparkSession.builder.appName("CreditCardFraudPreprocessing").getOrCreate()

    print(f"Loading data from {file_path}...")
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    print(f"Data loaded with schema: {df.printSchema()}")
    return df


def handle_missing_values(df: DataFrame, target_column: str) -> DataFrame:
    """
    Handle missing values in the dataset.
    Replace missing numerical values with the median
    and categorical values with the mode.
    """
    print("Handling missing values...")

    # Handle missing values for numerical columns
    numerical_cols = [
        field
        for field, dtype in df.dtypes
        if dtype in ["int", "double"] and field != target_column
    ]
    for col_name in numerical_cols:
        median_value = df.approxQuantile(col_name, [0.5], 0)[0]
        df = df.withColumn(
            col_name,
            when(df[col_name].isNull(), lit(median_value)).otherwise(df[col_name]),
        )
        print(
            f"Replaced missing values in numerical column '{col_name}' with median: {median_value}"
        )

    # Handle missing values for categorical columns
    categorical_cols = [field for field, dtype in df.dtypes if dtype == "string"]
    for col_name in categorical_cols:
        mode_value = (
            df.groupBy(col_name).count().orderBy("count", ascending=False).first()[0]
        )
        df = df.fillna({col_name: mode_value})
        print(
            f"Replaced missing values in categorical column '{col_name}' with mode: {mode_value}"
        )

    print("Missing values handled.")
    return df


def scale_features(df: DataFrame, numerical_columns: list) -> DataFrame:
    """
    Scale numerical features using StandardScaler.
    """
    print("Scaling features...")
    assembler = VectorAssembler(inputCols=numerical_columns, outputCol="features")
    scaler = StandardScaler(inputCol="features", outputCol="scaled_features")

    # Assemble and scale features
    assembled_df = assembler.transform(df)
    scaled_df = scaler.fit(assembled_df).transform(assembled_df)
    print("Features scaled.")
    return scaled_df


def split_data(df: DataFrame, test_size: float = 0.3, seed: int = 42):
    """
    Split the dataset into training and testing sets.
    """
    print("Splitting data into training and testing sets...")
    train_df, test_df = df.randomSplit([1 - test_size, test_size], seed=seed)
    print(
        f"Data split complete. Training data: {train_df.count()}, Testing data: {test_df.count()}"
    )
    return train_df, test_df


def save_preprocessed_data(train_df: DataFrame, test_df: DataFrame, output_dir: str):
    """
    Save the preprocessed data to Parquet files.
    """
    print(f"Saving preprocessed data to {output_dir}...")
    train_df.write.mode("overwrite").parquet(f"{output_dir}/train")
    test_df.write.mode("overwrite").parquet(f"{output_dir}/test")
    print("Preprocessed data saved.")


if __name__ == "__main__":
    # Example workflow
    DATA_PATH = "data/raw/creditcard.csv"
    TARGET_COLUMN = "Class"  # Update this with the correct target column name
    PROCESSED_DIR = "data/processed"

    # Load data
    data = load_data(DATA_PATH)

    # Handle missing values
    data = handle_missing_values(data, TARGET_COLUMN)

    # Scale numerical features
    numerical_features = [
        field
        for field, dtype in data.dtypes
        if dtype in ["int", "double"] and field != TARGET_COLUMN
    ]
    data = scale_features(data, numerical_features)

    # Split data into train and test sets
    train_data, test_data = split_data(data)

    # Save preprocessed data
    save_preprocessed_data(train_data, test_data, PROCESSED_DIR)
