from unittest.mock import Mock

import pytest
import requests

from tools.client import AdanosClient, AdanosError, build_window

TEST_CREDENTIAL = "x" * 8


def response(*, status: int = 200, payload: object | None = None) -> Mock:
    mock = Mock()
    mock.ok = 200 <= status < 300
    mock.status_code = status
    mock.json.return_value = payload if payload is not None else {"ok": True}
    return mock


def client(mock_response: Mock) -> tuple[AdanosClient, Mock]:
    session = Mock(spec=requests.Session)
    session.get.return_value = mock_response
    return AdanosClient(f" {TEST_CREDENTIAL} ", session=session), session


def test_stock_sentiment_routes_to_selected_source() -> None:
    api, session = client(response(payload={"ticker": "AAPL"}))

    result = api.get_stock_sentiment(
        "$aapl", source="NEWS", from_date="2026-07-01", to_date="2026-07-05"
    )

    assert result == {"ticker": "AAPL"}
    session.get.assert_called_once()
    request = session.get.call_args
    assert request.args == ("https://api.adanos.org/news/stocks/v1/stock/AAPL",)
    assert request.kwargs["headers"]["Accept"] == "application/json"
    assert request.kwargs["headers"]["X-API-Key"] == TEST_CREDENTIAL
    assert request.kwargs["params"] == {"from": "2026-07-01", "to": "2026-07-05"}
    assert request.kwargs["timeout"] == 15.0


def test_crypto_trending_ignores_stock_source() -> None:
    api, session = client(response(payload=[{"symbol": "BTC"}]))

    result = api.get_trending(asset_type="CRYPTO", source="polymarket", limit="3")

    assert result == [{"symbol": "BTC"}]
    assert session.get.call_args.args[0] == "https://api.adanos.org/reddit/crypto/v1/trending"
    assert session.get.call_args.kwargs["params"] == {"limit": 3}


@pytest.mark.parametrize("limit", [0, 2.5, 101, "many"])
def test_trending_rejects_invalid_limits(limit: object) -> None:
    api, session = client(response())

    with pytest.raises(ValueError, match="1 to 100"):
        api.get_trending(limit=limit)

    session.get.assert_not_called()


def test_window_validates_dates_and_order() -> None:
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        build_window("07/01/2026")
    with pytest.raises(ValueError, match="must not be after"):
        build_window("2026-07-05", "2026-07-01")


def test_api_key_failure_does_not_expose_key() -> None:
    api, _ = client(response(status=401))

    with pytest.raises(AdanosError, match="key was rejected") as exc_info:
        api.get_market_sentiment()

    assert TEST_CREDENTIAL not in str(exc_info.value)


def test_network_failure_uses_safe_message() -> None:
    session = Mock(spec=requests.Session)
    session.get.side_effect = requests.Timeout("request included sensitive context")
    api = AdanosClient(TEST_CREDENTIAL, session=session)

    with pytest.raises(AdanosError, match="request failed") as exc_info:
        api.get_crypto_sentiment("BTC")

    assert TEST_CREDENTIAL not in str(exc_info.value)
