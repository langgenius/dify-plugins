from enum import Enum
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests


class Endpoint(Enum):
    """
    An enumeration representing API endpoints for the Financial Datasets API.
    """

    COMPANY_FACTS = "/company/facts"
    CRYPTO_PRICES = "/crypto/prices"
    CRYPTO_SNAPSHOT = "/crypto/prices/snapshot"
    EARNINGS_PRESS_RELEASES = "/earnings/press-releases"
    FINANCIAL_METRICS_HISTORICAL = "/financial-metrics"
    FINANCIAL_METRICS_SNAPSHOT = "/financial-metrics/snapshot"
    FINANCIAL_STATEMENTS = "/financials"
    INSIDER_TRADES = "/insider-trades"
    INSTITUTIONAL_OWNERSHIP = "/institutional-ownership"
    COMPANY_NEWS = "/news"
    STOCK_PRICES = "/prices"
    STOCK_SNAPSHOT = "/prices/snapshot"
    SEC_FILINGS = "/filings"
    SEC_FILINGS_ITEMS = "/filings/items"


BASE_URL = "https://api.financialdatasets.ai/"


class FinancialDatasetsAPIError(Exception):
    """Custom exception for Financial Datasets API errors."""
    pass


def _is_request_successful(response: requests.Response) -> bool:
    """
    Checks if the HTTP response status code indicates success (2xx).

    Args:
        response (requests.Response): The response object from the request.

    Returns:
        bool: True if the status code is in the 200s, False otherwise.
    """
    return 200 <= response.status_code < 300


def _handle_api_response(response: requests.Response) -> str:
    """
    Handles the API response, raising an exception for unsuccessful requests.

    Args:
        response (requests.Response): The response object from the request.

    Returns:
        str: The response text from the API if successful.

    Raises:
        FinancialDatasetsAPIError: If the request was not successful.
    """
    if not _is_request_successful(response):
        raise FinancialDatasetsAPIError(
            f"API request failed with status code {response.status_code}: {response.text}"
        )
    return response.text


def _send_request(
    method: str,
    credentials: Dict[str, Any],
    endpoint: Endpoint,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Internal helper to send an HTTP request (GET or POST) to the API.

    Args:
        method (str): The HTTP method to use ('GET' or 'POST').
        credentials (Dict[str, Any]): A dictionary containing the API credentials,
            must include "financial_datasets_api_key".
        endpoint (Endpoint): The API endpoint.
        params (Optional[Dict[str, Any]]): Dictionary of query parameters for GET requests.
        data (Optional[Dict[str, Any]]): Dictionary of JSON data for POST requests.

    Returns:
        str: The response text from the API.

    Raises:
        FinancialDatasetsAPIError: If there's a network error, invalid credentials,
                                  or an unsuccessful API response.
    """
    api_key = credentials.get("financial_datasets_api_key")
    if not api_key:
        raise ValueError("Missing 'financial_datasets_api_key' in credentials.")

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }

    url = urljoin(BASE_URL, endpoint.value)

    try:
        if method == "GET":
            # Filter out None values from params for GET requests
            filtered_params = {k: v for k, v in (params or {}).items() if v is not None}
            response = requests.get(url, params=filtered_params, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        return _handle_api_response(response)

    except requests.exceptions.RequestException as e:
        raise FinancialDatasetsAPIError(f"Network error during API request: {e}")
    except Exception as e:
        raise FinancialDatasetsAPIError(f"An unexpected error occurred: {e}")


def http_get(credentials: Dict[str, Any], endpoint: Endpoint, params: Dict[str, Any]) -> str:
    """
    Sends a GET request to the specified endpoint.

    Args:
        credentials (Dict[str, Any]): A dictionary containing the API credentials.
            Must include the key "financial_datasets_api_key".
        endpoint (Endpoint): The endpoint to which the request will be sent.
            Should be an instance of the `Endpoint` enum.
        params (Dict[str, Any]): A dictionary of query parameters to include in the request.
            Parameters with `None` values will be excluded.

    Returns:
        str: The response text from the API.

    Raises:
        FinancialDatasetsAPIError: If there is an error sending the request or processing the response.
        ValueError: If 'financial_datasets_api_key' is missing from credentials.
    """
    return _send_request("GET", credentials, endpoint, params=params)


def http_post(credentials: Dict[str, Any], endpoint: Endpoint, data: Dict[str, Any]) -> str:
    """
    Sends a POST request to the specified endpoint.

    Args:
        credentials (Dict[str, Any]): A dictionary containing the API credentials.
            Must include the key "financial_datasets_api_key".
        endpoint (Endpoint): The endpoint to which the request will be sent.
            Should be an instance of the `Endpoint` enum.
        data (Dict[str, Any]): A dictionary of data to include in the request body.

    Returns:
        str: The response text from the API.

    Raises:
        FinancialDatasetsAPIError: If there is an error sending the request or processing the response.
        ValueError: If 'financial_datasets_api_key' is missing from credentials.
    """
    return _send_request("POST", credentials, endpoint, data=data)


def get_required_parameter(tool_parameters: Dict[str, Any], parameter: str) -> Any:
    """
    Retrieves a required parameter from a dictionary, raising an error if missing.

    Args:
        tool_parameters (Dict[str, Any]): A dictionary containing the parameters
            required for the tool's operation.
        parameter (str): The name of the parameter to retrieve.

    Returns:
        Any: The value of the specified parameter.

    Raises:
        ValueError: If the specified parameter is missing from `tool_parameters`.
    """
    if parameter not in tool_parameters:
        available_params = ", ".join(tool_parameters.keys()) if tool_parameters else "None"
        raise ValueError(
            f"Missing required parameter: '{parameter}'. Available parameters are: {available_params}"
        )
    return tool_parameters[parameter]