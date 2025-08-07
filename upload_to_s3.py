import boto3
import os
import sys
from dotenv import load_dotenv

def upload_file_to_s3(local_path, bucket_name, s3_key):
    s3 = boto3.client('s3')
    s3.upload_file(local_path, bucket_name, s3_key)
    print(f"Uploaded {local_path} to s3://{bucket_name}/{s3_key}")

if __name__ == "__main__":
    load_dotenv()
    bucket_name = os.environ.get("AWS_S3_BUCKET")
    default_s3_key = os.environ.get("TITANIC_DATA_KEY", "datasets/titanic.csv")

    if not bucket_name:
        raise ValueError("AWS_S3_BUCKET env variable is not set")

    # Використання аргументів командного рядка
    # python upload_to_s3.py [local_path] [s3_key]
    local_path = sys.argv[1] if len(sys.argv) > 1 else "titanic.csv"
    s3_key = sys.argv[2] if len(sys.argv) > 2 else default_s3_key

    upload_file_to_s3(local_path, bucket_name, s3_key)