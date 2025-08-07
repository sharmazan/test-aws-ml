from __future__ import annotations

import json
import random
import boto3
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

from config import get_settings
from s3_utils import read_csv


def main() -> None:
    load_dotenv()
    settings = get_settings()

    df = read_csv(settings.aws_s3_bucket, settings.titanic_data_path)
    df = df.dropna(subset=["Survived", "Pclass", "Sex", "Age"])

    info_cols = ["Name", "Pclass", "Sex", "Age", "Survived"]
    info_df = df[info_cols].copy()

    df["Sex"] = df["Sex"].map({"male": 0, "female": 1})
    X = df[["Pclass", "Sex", "Age"]]
    y = df["Survived"]

    _, X_test, _, _, _, info_test = train_test_split(
        X, y, info_df, test_size=0.2, random_state=42
    )

    idx = random.randrange(len(X_test))
    features = X_test.iloc[idx]
    person = info_test.iloc[idx]

    print("Random test passenger:")
    print(f"Name: {person['Name']}")
    print(f"Pclass: {person['Pclass']}")
    print(f"Sex: {person['Sex']}")
    print(f"Age: {person['Age']}")

    payload = {
        "Pclass": int(features["Pclass"]),
        "Sex": int(features["Sex"]),
        "Age": float(features["Age"]),
    }

    client = boto3.client("lambda")
    response = client.invoke(
        FunctionName=settings.lambda_function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload).encode(),
    )
    result = json.loads(response["Payload"].read())
    prediction = int(result.get("prediction", 0))

    pred_str = "survived" if prediction == 1 else "did not survive"
    actual_str = "survived" if int(person["Survived"]) == 1 else "did not survive"
    print(f"Lambda prediction: passenger {pred_str}.")
    print(f"Actual outcome: passenger {actual_str}.")


if __name__ == "__main__":
    main()
