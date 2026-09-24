import json
from typing import Any, Generator
from urllib.parse import urlparse

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

MAX_RESPONSE_BYTES = 100_000
ALLOWED_SCHEMES = {"http", "https"}


class X402CallTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        url = (tool_parameters.get("url") or "").strip()
        parsed = urlparse(url)
        if parsed.scheme not in ALLOWED_SCHEMES or not parsed.netloc:
            yield self.create_text_message(
                f"Refusing to call '{url}': only http:// and https:// URLs are supported."
            )
            return

        method = (tool_parameters.get("method") or "GET").upper()
        if method not in {"GET", "POST"}:
            method = "GET"

        query_params = None
        if tool_parameters.get("query_params"):
            try:
                query_params = json.loads(tool_parameters["query_params"])
            except json.JSONDecodeError as e:
                yield self.create_text_message(f"Invalid JSON in Query Parameters: {e}")
                return

        json_body = None
        if method == "POST" and tool_parameters.get("json_body"):
            try:
                json_body = json.loads(tool_parameters["json_body"])
            except json.JSONDecodeError as e:
                yield self.create_text_message(f"Invalid JSON in JSON Body: {e}")
                return

        headers = {"Accept": "application/json", "User-Agent": "dify-x402-pay-per-call"}
        if tool_parameters.get("payment_header"):
            headers["X-PAYMENT"] = tool_parameters["payment_header"].strip()
        if tool_parameters.get("balance_account"):
            headers["X-BALANCE"] = tool_parameters["balance_account"].strip()

        timeout = tool_parameters.get("timeout") or 30

        try:
            response = requests.request(
                method=method,
                url=url,
                params=query_params,
                json=json_body,
                headers=headers,
                timeout=timeout,
                allow_redirects=False,
            )
        except requests.RequestException as e:
            yield self.create_text_message(f"Request to '{url}' failed: {e}")
            return

        body_text = response.text[:MAX_RESPONSE_BYTES]
        try:
            payload = json.loads(body_text)
        except json.JSONDecodeError:
            payload = None

        if response.status_code == 200:
            result = {"status": 200, "body": payload if payload is not None else body_text}
            yield self.create_json_message(result)
            yield self.create_text_message(
                json.dumps(payload, ensure_ascii=False, indent=2)
                if payload is not None
                else body_text
            )
            return

        if response.status_code == 402:
            challenge = payload if isinstance(payload, dict) else {}
            result = {
                "status": 402,
                "payment_required": True,
                "price": challenge.get("price_xno", challenge.get("price")),
                "pay_to": challenge.get("pay_to"),
                "accepts": challenge.get("accepts", []),
                "raw": challenge or body_text,
            }
            yield self.create_json_message(result)
            price = result["price"]
            pay_to = result["pay_to"]
            if price and pay_to:
                explanation = (
                    f"Payment required: send {price} XNO to {pay_to} from any Nano "
                    "wallet, then call this tool again with the resulting settled "
                    "block hash as 'Payment Proof (Nano block hash)'."
                )
            else:
                explanation = (
                    "Payment required, but the endpoint did not quote a standard "
                    "price/pay-to pair. See the raw challenge for details."
                )
            yield self.create_text_message(explanation)
            return

        yield self.create_json_message({"status": response.status_code, "body": body_text})
        yield self.create_text_message(
            f"Endpoint answered HTTP {response.status_code}:\n{body_text}"
        )
