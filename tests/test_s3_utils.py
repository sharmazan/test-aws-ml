from __future__ import annotations

import io
from unittest.mock import MagicMock

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from s3_utils import load_pickle, read_csv, save_pickle


def test_read_csv(monkeypatch):
    df = pd.DataFrame({"a": [1]})
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)

    mock_s3 = MagicMock()
    mock_s3.get_object.return_value = {"Body": io.BytesIO(buf.getvalue())}
    monkeypatch.setattr("s3_utils._s3", mock_s3)

    loaded = read_csv("bucket", "key")
    assert loaded.equals(df)
    mock_s3.get_object.assert_called_once_with(Bucket="bucket", Key="key")


def test_save_and_load_pickle(monkeypatch):
    store: dict[tuple[str, str], bytes] = {}

    def put_object(*, Bucket: str, Key: str, Body: bytes):
        store[(Bucket, Key)] = Body

    def get_object(*, Bucket: str, Key: str):
        return {"Body": io.BytesIO(store[(Bucket, Key)])}

    mock_s3 = MagicMock()
    mock_s3.put_object.side_effect = put_object
    mock_s3.get_object.side_effect = get_object
    monkeypatch.setattr("s3_utils._s3", mock_s3)

    obj = {"x": 1}
    save_pickle(obj, "b", "k")
    loaded = load_pickle("b", "k")
    assert loaded == obj
    mock_s3.put_object.assert_called_once()
    mock_s3.get_object.assert_called_once()
