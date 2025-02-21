import requests


TOKEN_URL = "https://api.dingtalk.com/v1.0/oauth2/accessToken"


class DingTalkAccessTokenError(Exception):
    pass


def get_access_token(app_key: str, app_secret: str) -> str:
    try:
        access_token, expires_in = _fetch_access_token(app_key, app_secret)
        return access_token
    except Exception as e:
        raise DingTalkAccessTokenError(f"Failed to obtain access token: {str(e)}") from e


def _fetch_access_token(app_key: str, app_secret: str) -> tuple:
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "appKey": app_key,
        "appSecret": app_secret
    }

    try:
        response = requests.post(TOKEN_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'accessToken' not in data or 'expireIn' not in data:
            error_msg = data.get("errmsg", "Missing accessToken or expireIn fields")
            raise DingTalkAccessTokenError(f"Failed to obtain access token: {error_msg}")

        access_token = data['accessToken']
        expires_in = data['expireIn']

        return access_token, expires_in

    except requests.RequestException as e:
        raise DingTalkAccessTokenError(f"HTTP request error: {str(e)}") from e
    except ValueError:
        raise DingTalkAccessTokenError("Response content is not valid JSON") from ValueError
