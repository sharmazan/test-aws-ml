#!/bin/bash

# Try to find mlflow in PATH or in .venv/bin
if command -v mlflow &> /dev/null; then
    MLFLOW_CMD="mlflow"
elif [ -x "./.venv/bin/mlflow" ]; then
    MLFLOW_CMD="./.venv/bin/mlflow"
else
    echo "MLflow is not installed or not in PATH."
    echo "Install it with: pip install mlflow"
    exit 1
fi

# Start MLflow server with local file storage
$MLFLOW_CMD server \
    --backend-store-uri ./mlruns \
    --default-artifact-root ./mlruns \
    --host 0.0.0.0 \
    --port 5000