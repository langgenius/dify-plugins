from typing import Any

import requests


def search(credentials: dict[str, Any], parameters: dict[str, Any], endpoint: str) -> dict:
    key = credentials.get("api_key")
    if not key:
        raise ValueError("A SerpKite API key is required.")
    query = parameters.get("query")
    if not isinstance(query, str) or not query.strip():
        raise ValueError("A non-empty search query is required.")
    params: dict[str, Any] = {"q": query}
    for name in ("country", "language", "time"):
        value = parameters.get(name)
        if value:
            params[name] = value
    if "num" in parameters and parameters["num"] is not None:
        value = parameters["num"]
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value != int(value) or not 1 <= value <= 100:
            raise ValueError("Number of results must be an integer from 1 to 100.")
        params["num"] = int(value)
    try:
        response = requests.get(
            f"https://api.serpkite.com/v1/{endpoint}",
            headers={"Authorization": f"Bearer {key}"},
            params=params,
            timeout=90,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        raise ValueError("SerpKite search failed. Check credits, rate limits, and service status.") from None


def markdown(payload: dict) -> str:
    results = payload.get("results", [])
    if not results:
        return "No results found."
    lines = []
    for index, item in enumerate(results, 1):
        title = str(item.get("title") or "Untitled").replace("[", r"\[").replace("]", r"\]")
        link = str(item.get("link") or "").replace("(", "%28").replace(")", "%29")
        lines.append(f"{index}. [{title}]({link})")
        if item.get("snippet"):
            lines.append(str(item["snippet"]))
        lines.append("")
    return "\n".join(lines).rstrip()
