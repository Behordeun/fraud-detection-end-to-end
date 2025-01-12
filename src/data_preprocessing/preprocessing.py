from pyspark.ml.feature import StandardScaler, VectorAssembler
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, lit, udf, when
from pyspark.sql.types import DoubleType


def load_data(file_path: str) -> DataFrame:
    """
    Load the dataset from a CSV file.
    """
    spark = SparkSession.builder.appName("CreditCardFraudPreprocessing").getOrCreate()

    print(f"Loading data from {file_path}...")
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    print("Data loaded with schema:")
    df.printSchema()
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
        mode_row = (
            df.groupBy(col_name).count().orderBy("count", ascending=False).first()
        )
        if mode_row:
            mode_value = mode_row[0] if mode_row[0] is not None else "Unknown"
        else:
            mode_value = "Unknown"  # Fallback value
        print(f"Calculated mode for column '{col_name}': {mode_value}")
        df = df.fillna({col_name: mode_value})
        print(
            f"Replaced missing values in categorical column '{col_name}' with mode: {mode_value}"
        )

    print("Missing values handled.")
    return df


def scale_amount_column(df: DataFrame) -> DataFrame:
    """
    Scale the 'Amount' column using StandardScaler and overwrite it with the scaled scalar values.
    """
    print("Scaling the 'Amount' column...")

    # Assemble the Amount column into a feature vector
    assembler = VectorAssembler(inputCols=["Amount"], outputCol="Amount_feature")
    df = assembler.transform(df)

    # Apply StandardScaler to the Amount feature
    scaler = StandardScaler(
        inputCol="Amount_feature",
        outputCol="scaled_Amount",
        withMean=True,
        withStd=True,
    )
    scaler_model = scaler.fit(df)
    df = scaler_model.transform(df)

    # Extract the first (and only) value from the DenseVector using a UDF
    def extract_scalar(value):
        return float(value[0])  # Extract the first element from the vector

    extract_scalar_udf = udf(extract_scalar, DoubleType())
    df = df.withColumn("Amount", extract_scalar_udf(col("scaled_Amount")))

    # Drop the temporary columns
    df = df.drop("Amount_feature", "scaled_Amount")
    print("Scaled 'Amount' column converted to scalar and updated the dataset.")

    return df


def drop_unnecessary_columns(df: DataFrame) -> DataFrame:
    """
    Drop columns that are not useful for modeling (e.g., 'id').
    """
    columns_to_drop = ["id"]  # Add any other unnecessary columns here if needed
    print(f"Dropping unnecessary columns: {columns_to_drop}")
    for col in columns_to_drop:
        if col in df.columns:
            df = df.drop(col)
    print("Unnecessary columns dropped.")
    return df


def set_features_and_target(df: DataFrame, target_column: str) -> DataFrame:
    """
    Add 'features' column while retaining the original variables in the schema.
    """
    print("Setting feature variables and target variable...")

    # All columns except the target column are features
    feature_columns = [col for col in df.columns if col != target_column]

    print(f"Feature columns: {feature_columns}")
    print(f"Target column: {target_column}")

    # Use VectorAssembler to combine feature variables into a single feature vector
    assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
    df = assembler.transform(df)

    print("Features column added to the dataset while retaining the original columns.")
    return df


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
    DATA_PATH = "data/raw/creditcard_2023.csv"
    TARGET_COLUMN = "Class"  # Update this with the correct target column name
    PROCESSED_DIR = "data/processed"

    # Load data
    data = load_data(DATA_PATH)

    # Drop unnecessary columns
    data = drop_unnecessary_columns(data)

    # Handle missing values
    data = handle_missing_values(data, TARGET_COLUMN)

    # Scale the 'Amount' column
    data = scale_amount_column(data)

    # Ensure the 'Class' column is retained in the processed data
    if TARGET_COLUMN not in data.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' is missing from the processed dataset!"
        )

    # Add 'features' column while retaining original variables
    data = set_features_and_target(data, TARGET_COLUMN)

    # Split data into train and test sets
    train_data, test_data = split_data(data)

    # Save preprocessed data
    save_preprocessed_data(train_data, test_data, PROCESSED_DIR)
