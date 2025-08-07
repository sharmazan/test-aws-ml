from __future__ import annotations

from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier

from config import get_settings
from download_titanic import download_titanic_csv
from s3_utils import read_csv, save_pickle, upload_file


def main() -> None:
    load_dotenv()
    settings = get_settings()

    # Download dataset
    download_titanic_csv()
    print("Titanic dataset downloaded.")

    # Upload dataset to S3
    upload_file("titanic.csv", settings.aws_s3_bucket, settings.titanic_data_path)
    print(
        f"Titanic dataset uploaded to s3://{settings.aws_s3_bucket}/{settings.titanic_data_path}"
    )

    # Read dataset from S3
    df = read_csv(settings.aws_s3_bucket, settings.titanic_data_path)
    df = df.dropna(subset=["Survived", "Pclass", "Sex", "Age"])
    df["Sex"] = df["Sex"].map({"male": 0, "female": 1})
    X = df[["Pclass", "Sex", "Age"]]
    y = df["Survived"]

    # Train model
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)

    # Save model to S3
    save_pickle(clf, settings.aws_s3_bucket, settings.model_s3_path)
    print(f"Model uploaded to s3://{settings.aws_s3_bucket}/{settings.model_s3_path}")


if __name__ == "__main__":
    main()
