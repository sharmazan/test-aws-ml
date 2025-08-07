from __future__ import annotations

from dotenv import load_dotenv
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from config import get_settings
from s3_utils import read_csv


def main() -> None:
    load_dotenv()
    settings = get_settings()
    mlflow.set_tracking_uri(settings.mlflow_url)

    df = read_csv(settings.aws_s3_bucket, settings.titanic_data_key)
    df = df.dropna(subset=["Survived", "Pclass", "Sex", "Age"])
    df["Sex"] = df["Sex"].map({"male": 0, "female": 1})
    X = df[["Pclass", "Sex", "Age"]]
    y = df["Survived"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    with mlflow.start_run():
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)
        acc = accuracy_score(y_test, preds)

        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("accuracy", acc)
        mlflow.sklearn.log_model(clf, "model")

    print(f"Accuracy: {acc}")


if __name__ == "__main__":
    main()
