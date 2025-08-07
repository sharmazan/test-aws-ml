from __future__ import annotations

import io
import pickle
from typing import Any

import boto3
import pandas as pd

_s3 = boto3.client("s3")


def upload_file(local_path: str, bucket: str, key: str) -> None:
    """Upload a local file to S3."""
    _s3.upload_file(local_path, bucket, key)


def read_csv(bucket: str, key: str) -> pd.DataFrame:
    obj = _s3.get_object(Bucket=bucket, Key=key)
    return pd.read_csv(io.BytesIO(obj["Body"].read()))


def save_pickle(obj: Any, bucket: str, key: str) -> None:
    buf = io.BytesIO()
    pickle.dump(obj, buf)
    buf.seek(0)
    _s3.put_object(Bucket=bucket, Key=key, Body=buf.getvalue())


def load_pickle(bucket: str, key: str) -> Any:
    obj = _s3.get_object(Bucket=bucket, Key=key)
    return pickle.load(io.BytesIO(obj["Body"].read()))
