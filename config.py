from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass
class Settings:
    aws_s3_bucket: str
    titanic_data_path: str = "datasets/titanic.csv"
    model_s3_path: str = "models/titanic_rf.pkl"
    mlflow_url: str = "http://127.0.0.1:5000"
    lambda_function_name: str = "titanic-train"


def _get_env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None:
        raise EnvironmentError(f"{name} env variable is not set")
    return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings(
        aws_s3_bucket=_get_env("AWS_S3_BUCKET"),
        titanic_data_path=os.environ.get("TITANIC_DATA_PATH", "datasets/titanic.csv"),
        model_s3_path=os.environ.get("MODEL_S3_PATH", "models/titanic_rf.pkl"),
        mlflow_url=os.environ.get("MLFLOW_URL", "http://127.0.0.1:5000"),
        lambda_function_name=os.environ.get("LAMBDA_FUNCTION_NAME", "titanic-train"),
    )
