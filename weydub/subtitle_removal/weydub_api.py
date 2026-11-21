import hashlib
import json
import re
from urllib.parse import urlsplit

import requests


class ApiError(RuntimeError):
    pass


def direct_url(value):
    try:
        parts = urlsplit(value)
        return bool(parts.scheme == "https" and parts.hostname and
                    parts.username is None and parts.password is None and
                    not re.search(r"[\s\\\x00-\x1f]", value))
    except (ValueError, TypeError, AttributeError):
        return False


def call(credentials, path, payload):
    key, secret = credentials.get("app_key"), credentials.get("app_secret")
    if not key or not secret:
        raise ApiError("Set both Weydub credentials in the tool provider settings.")
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    inner = hashlib.md5(data).hexdigest()
    sign = hashlib.md5((inner + secret).encode()).hexdigest()
    try:
        response = requests.post("https://api.zhaoli.com/v-w-c/gateway/ve/" + path,
                                 data=data, headers={"AppKey": key, "AppSign": sign,
                                                     "Content-Type": "application/json"},
                                 timeout=(8, 35), allow_redirects=False)
        if response.status_code != 200:
            raise ApiError(f"Weydub returned HTTP {response.status_code}.")
        value = response.json()
    except (requests.RequestException, ValueError):
        raise ApiError("Weydub did not return a readable response.") from None
    if not isinstance(value, dict) or value.get("code") != 1000:
        code = value.get("code") if isinstance(value, dict) else None
        raise ApiError(f"Weydub rejected the request (code {code if type(code) is int else 'unknown'}).")
    return value.get("body")


def submit(credentials, video_url):
    if not direct_url(video_url):
        raise ApiError("Provide a direct HTTPS video URL without embedded credentials.")
    try:
        body = call(credentials, "work/free", {
            "urls": [video_url], "needChineseOcclude": 1, "videoInpaintLang": "all",
            "extraOptions": '{"extra_inpaint_config":{"model":"advanced_full"}}',
        })
        work_id = str(body["dataList"][0]["id"])
        if not re.fullmatch("[1-9][0-9]*", work_id):
            raise ApiError("No confirmed work ID.")
        return work_id
    except (ApiError, KeyError, TypeError, IndexError) as exc:
        reason = str(exc) if isinstance(exc, ApiError) else "No confirmed work ID."
        raise ApiError(f"{reason} Check your Weydub job history before submitting again.") from None


def status(credentials, work_id):
    if not isinstance(work_id, str) or not re.fullmatch("[1-9][0-9]*", work_id):
        raise ApiError("Use the numeric work ID returned by the submission.")
    body = call(credentials, "work/status", {"idWorks": [work_id]})
    rows = body.get("content") if isinstance(body, dict) else None
    row = next((r for r in rows if isinstance(r, dict) and str(r.get("id")) == work_id),
               None) if isinstance(rows, list) else None
    if not row or type(row.get("processStatus")) is not int:
        raise ApiError("No matching work status. Use the same account that submitted the video.")
    code = row["processStatus"]
    if code == 1:
        url = row.get("videoUrl")
        if isinstance(url, str) and url.startswith("http://"):
            url = "https://" + url[7:]
        if not direct_url(url):
            raise ApiError("Processing finished without a usable link. Check this work ID in Weydub.")
        return {"state": "ready", "video_url": url}
    return {"state": "processing"} if code < 1 else {"state": "failed", "code": code}
