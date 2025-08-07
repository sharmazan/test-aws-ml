import boto3
import os
import io
import pickle
import pandas as pd
from dotenv import load_dotenv
from sklearn.ensemble import RandomForestClassifier

def read_csv_from_s3(bucket, key):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj['Body'].read()))

def save_model_to_s3(model, bucket, key):
    s3 = boto3.client('s3')
    buf = io.BytesIO()
    pickle.dump(model, buf)
    buf.seek(0)
    s3.put_object(Bucket=bucket, Key=key, Body=buf.getvalue())

def lambda_handler(event, context):
    load_dotenv()
    bucket = os.environ.get("AWS_S3_BUCKET")
    data_key = os.environ.get("TITANIC_DATA_KEY", "datasets/titanic.csv")
    model_key = os.environ.get("MODEL_S3_KEY", "models/titanic_rf.pkl")

    df = read_csv_from_s3(bucket, data_key)
    df = df.dropna(subset=['Survived', 'Pclass', 'Sex', 'Age'])
    df['Sex'] = df['Sex'].map({'male': 0, 'female': 1})
    X = df[['Pclass', 'Sex', 'Age']]
    y = df['Survived']

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)

    save_model_to_s3(clf, bucket, model_key)
    return {"status": "ok", "model_key": model_key}
