"""Fixture."""

import json
from pathlib import Path

import pytest
from creality_wifi_box_client.creality_wifi_box_client import BoxInfo


@pytest.fixture
def mock_box_info() -> BoxInfo:
    """Load BoxInfo data from JSON fixture."""
    file_path = Path(__file__).parent / "fixtures" / "mock_box_info.json"
    content = file_path.read_text(encoding="utf-8")
    data = json.loads(content)

    return BoxInfo(**data)
