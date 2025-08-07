import argparse
from dotenv import load_dotenv

from config import get_settings
from s3_utils import upload_file


def main() -> None:
    load_dotenv()
    settings = get_settings()

    parser = argparse.ArgumentParser(description="Upload a file to S3")
    parser.add_argument("local_path", nargs="?", default="titanic.csv")
    parser.add_argument("s3_path", nargs="?", default=settings.titanic_data_path)
    args = parser.parse_args()

    upload_file(args.local_path, settings.aws_s3_bucket, args.s3_path)
    print(f"Uploaded {args.local_path} to s3://{settings.aws_s3_bucket}/{args.s3_path}")


if __name__ == "__main__":
    main()
