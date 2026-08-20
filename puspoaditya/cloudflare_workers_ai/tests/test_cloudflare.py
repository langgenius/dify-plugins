import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models.llm.llm import CloudflareLargeLanguageModel  # noqa: E402


def test_add_custom_parameters_builds_openai_compatible_endpoint():
    credentials = {"account_id": "abc123", "api_key": "test-token"}
    CloudflareLargeLanguageModel._add_custom_parameters(credentials)

    assert credentials["mode"] == "chat"
    assert credentials["endpoint_url"] == (
        "https://api.cloudflare.com/client/v4/accounts/abc123/ai/v1"
    )


def test_add_custom_parameters_requires_account_id():
    with pytest.raises(ValueError, match="Account ID"):
        CloudflareLargeLanguageModel._add_custom_parameters({"api_key": "x"})
