from __future__ import annotations

import pytest

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import get_settings


def test_missing_bucket(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.delenv("AWS_S3_BUCKET", raising=False)
    with pytest.raises(EnvironmentError):
        get_settings()
