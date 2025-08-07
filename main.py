import boto3
import os
from dotenv import load_dotenv

from download_titanic import download_titanic_csv
from upload_to_s3 import upload_file_to_s3


def invoke_lambda(lambda_name):
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName=lambda_name,
        InvocationType='RequestResponse'
    )
    return response['Payload'].read()


def download_model(bucket, model_key, local_path):
    s3 = boto3.client('s3')
    s3.download_file(bucket, model_key, local_path)
    print(f"Downloaded model to {local_path}")


load_dotenv()
bucket_name = os.environ.get("AWS_S3_BUCKET")
default_s3_key = os.environ.get("TITANIC_DATA_KEY", "datasets/titanic.csv")


def main():
    print("Hello from aws!")
    download_titanic_csv()
    print("Titanic dataset downloaded successfully.")
    upload_file_to_s3("titanic.csv", bucket_name, "datasets/titanic.csv")
    print("Titanic dataset uploaded to S3 successfully.")
    print("Run train_titanic.py to train the model.")

    lambda_name = os.environ.get("LAMBDA_FUNCTION_NAME", "titanic-train")
    model_key = os.environ.get("MODEL_S3_KEY", "models/titanic_rf.pkl")
    local_model = "titanic_rf.pkl"

    print("Invoking Lambda for training...")
    print(invoke_lambda(lambda_name))

    print("Downloading trained model...")
    download_model(bucket_name, model_key, local_model)

    print("Running prediction...")
    os.system(f"python predict.py titanic.csv predictions.csv")


if __name__ == "__main__":
    main()
