from __future__ import annotations

from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier

from config import get_settings
from s3_utils import read_csv, save_pickle


def lambda_handler(event, context):
    load_dotenv()
    settings = get_settings()

    df = read_csv(settings.aws_s3_bucket, settings.titanic_data_path)
    df = df.dropna(subset=["Survived", "Pclass", "Sex", "Age"])
    df["Sex"] = df["Sex"].map({"male": 0, "female": 1})
    X = df[["Pclass", "Sex", "Age"]]
    y = df["Survived"]

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)

    save_pickle(clf, settings.aws_s3_bucket, settings.model_s3_path)
    return {"status": "ok", "model_path": settings.model_s3_path}
