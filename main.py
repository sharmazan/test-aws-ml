from __future__ import annotations

import boto3
from dotenv import load_dotenv

from config import get_settings
from download_titanic import download_titanic_csv
from predict import main as run_prediction
from s3_utils import upload_file


def invoke_lambda(lambda_name: str) -> bytes:
    client = boto3.client("lambda")
    response = client.invoke(FunctionName=lambda_name, InvocationType="RequestResponse")
    return response["Payload"].read()


def download_model(bucket: str, model_path: str, local_path: str) -> None:
    s3 = boto3.client("s3")
    s3.download_file(bucket, model_path, local_path)
    print(f"Downloaded model to {local_path}")


def main() -> None:
    load_dotenv()
    settings = get_settings()

    print("Hello from aws!")
    download_titanic_csv()
    print("Titanic dataset downloaded successfully.")

    upload_file("titanic.csv", settings.aws_s3_bucket, settings.titanic_data_path)
    print("Titanic dataset uploaded to S3 successfully.")
    print("Run train_titanic.py to train the model.")

    print("Invoking Lambda for training...")
    print(invoke_lambda(settings.lambda_function_name))

    print("Downloading trained model...")
    download_model(settings.aws_s3_bucket, settings.model_s3_path, "titanic_rf.pkl")

    print("Running prediction...")
    run_prediction("titanic.csv", "predictions.csv")


if __name__ == "__main__":
    main()
