import boto3
import os
import io
import pickle
import pandas as pd
from dotenv import load_dotenv

def load_model_from_s3(bucket, key):
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=key)
    return pickle.load(io.BytesIO(obj['Body'].read()))

def main(input_csv, output_csv):
    load_dotenv()
    bucket = os.environ.get("AWS_S3_BUCKET")
    model_key = os.environ.get("MODEL_S3_KEY", "models/titanic_rf.pkl")

    model = load_model_from_s3(bucket, model_key)
    df = pd.read_csv(input_csv)
    df['Sex'] = df['Sex'].map({'male': 0, 'female': 1})
    X = df[['Pclass', 'Sex', 'Age']]
    preds = model.predict(X)
    df['prediction'] = preds
    df.to_csv(output_csv, index=False)
    print(f"Predictions saved to {output_csv}")

if __name__ == "__main__":
    import sys
    input_csv = sys.argv[1] if len(sys.argv) > 1 else "titanic.csv"
    output_csv = sys.argv[2] if len(sys.argv) > 2 else "predictions.csv"
    main(input_csv, output_csv)
