import boto3
import pandas as pd
import io
import os
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import mlflow
import mlflow.sklearn

def read_csv_from_s3(bucket, key):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj['Body'].read()))

if __name__ == "__main__":
    load_dotenv()  # Завантажити змінні з .env

    mlflow_url = os.environ.get("MLFLOW_URL", "http://127.0.0.1:5000")
    mlflow.set_tracking_uri(mlflow_url)

    bucket = os.environ.get("AWS_S3_BUCKET")
    key = os.environ.get("TITANIC_DATA_KEY", "datasets/titanic.csv")

    if not bucket:
        raise ValueError("AWS_S3_BUCKET env variable is not set")

    df = read_csv_from_s3(bucket, key)
    # Простий препроцесинг
    df = df.dropna(subset=['Survived', 'Pclass', 'Sex', 'Age'])
    df['Sex'] = df['Sex'].map({'male': 0, 'female': 1})
    X = df[['Pclass', 'Sex', 'Age']]
    y = df['Survived']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    with mlflow.start_run():
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        preds = clf.predict(X_test)
        acc = accuracy_score(y_test, preds)

        mlflow.log_param("n_estimators", 100)
        mlflow.log_metric("accuracy", acc)
        mlflow.sklearn.log_model(clf, "model")

        print(f"Accuracy: {acc}")