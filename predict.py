import argparse
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv
import pandas as pd

from config import get_settings
from s3_utils import load_pickle


def main(input_csv: str, output_csv: str) -> None:
    load_dotenv()
    settings = get_settings()

    try:
        model = load_pickle(settings.aws_s3_bucket, settings.model_s3_path)
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError("Failed to load model from S3") from exc

    df = pd.read_csv(input_csv)
    df = df.dropna(subset=["Pclass", "Sex", "Age"])
    df["Sex"] = df["Sex"].map({"male": 0, "female": 1})
    X = df[["Pclass", "Sex", "Age"]]
    preds = model.predict(X)
    df["prediction"] = preds
    df.to_csv(output_csv, index=False)
    print(f"Predictions saved to {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run predictions using a model stored in S3"
    )
    parser.add_argument("input_csv", nargs="?", default="titanic.csv")
    parser.add_argument("output_csv", nargs="?", default="predictions.csv")
    args = parser.parse_args()
    main(args.input_csv, args.output_csv)
