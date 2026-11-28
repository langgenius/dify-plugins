"""KontoCSV ToolProvider OAuth 2.0 with short-lived PKCE S256 state."""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlencode, urlsplit

import requests
from cryptography.fernet import Fernet, InvalidToken
from dify_plugin import ToolProvider
from dify_plugin.entities.oauth import ToolOAuthCredentials
from dify_plugin.errors.tool import ToolProviderCredentialValidationError, ToolProviderOAuthError

from tools.mcp_client import KontoCsvMcpError, call_mcp

AUTH_URL = "https://www.kontocsv.de/api/auth/oauth2/authorize"
TOKEN_URL = "https://www.kontocsv.de/api/auth/oauth2/token"
RESOURCE_URL = "https://www.kontocsv.de/api/mcp/claude"
SCOPES = "mcp:tools offline_access"


def _validate_callback(redirect_uri: str) -> bool:
    try:
        parsed = urlsplit(redirect_uri)
        return (parsed.scheme == "https" and bool(parsed.hostname) and
                not parsed.username and not parsed.password and
                not parsed.query and not parsed.fragment)
    except ValueError:
        return False


def _cipher(redirect_uri: str, client: Mapping[str, Any]) -> Fernet:
    client_id = client.get("client_id")
    client_secret = client.get("client_secret")
    if not isinstance(client_id, str) or not client_id or not isinstance(client_secret, str) or not client_secret:
        raise ToolProviderOAuthError("Configure the KontoCSV OAuth client ID and secret in Dify.")
    key = hmac.digest(
        client_secret.encode("utf-8"),
        b"kontocsv-dify-pkce-state-v1\x00" + client_id.encode("utf-8") +
        b"\x00" + redirect_uri.encode("utf-8"),
        "sha256",
    )
    return Fernet(base64.urlsafe_b64encode(key))


def _exchange_token(data: dict[str, str], client: Mapping[str, Any]) -> ToolOAuthCredentials:
    client_id = client.get("client_id")
    client_secret = client.get("client_secret")
    if not isinstance(client_id, str) or not client_id or not isinstance(client_secret, str) or not client_secret:
        raise ToolProviderOAuthError("Configure the KontoCSV OAuth client.")
    try:
        response = requests.post(
            TOKEN_URL, data=data, auth=(client_id, client_secret),
            timeout=(5, 15), allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise ToolProviderOAuthError("KontoCSV OAuth token service is unreachable.") from exc
    if response.status_code != 200:
        raise ToolProviderOAuthError("KontoCSV OAuth token exchange was rejected.")
    try:
        token = response.json()
    except ValueError as exc:
        raise ToolProviderOAuthError("KontoCSV returned an invalid OAuth token response.") from exc
    if not isinstance(token, dict) or not isinstance(token.get("access_token"), str):
        raise ToolProviderOAuthError("KontoCSV did not return an access token.")
    credentials = {"access_token": token["access_token"]}
    if isinstance(token.get("refresh_token"), str):
        credentials["refresh_token"] = token["refresh_token"]
    try:
        expires_at = int(time.time()) + max(60, int(token.get("expires_in", 3600)))
    except (ValueError, TypeError) as exc:
        raise ToolProviderOAuthError("KontoCSV returned an invalid token lifetime.") from exc
    return ToolOAuthCredentials(credentials=credentials, expires_at=expires_at)


class KontoCsvProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        if not credentials.get("access_token"):
            raise ToolProviderCredentialValidationError("Connect KontoCSV through OAuth.")
        try:
            call_mcp("get_credit_balance", {}, credentials["access_token"])
        except KontoCsvMcpError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc

    def _oauth_get_authorization_url(self, redirect_uri: str, system_credentials: Mapping[str, Any]) -> str:
        if not isinstance(redirect_uri, str) or not _validate_callback(redirect_uri):
            raise ToolProviderOAuthError("Dify must provide a secure OAuth callback URL.")
        verifier = secrets.token_urlsafe(48)
        challenge = base64.urlsafe_b64encode(
            hashlib.sha256(verifier.encode("ascii")).digest()
        ).rstrip(b"=").decode("ascii")
        state = _cipher(redirect_uri, system_credentials).encrypt(verifier.encode("ascii")).decode("ascii")
        return AUTH_URL + "?" + urlencode({
            "client_id": str(system_credentials["client_id"]),
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": SCOPES,
            "resource": RESOURCE_URL,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        })

    def _oauth_get_credentials(
        self, redirect_uri: str, system_credentials: Mapping[str, Any], request: Any
    ) -> ToolOAuthCredentials:
        if request.args.get("error"):
            raise ToolProviderOAuthError("KontoCSV authorization was declined.")
        code = request.args.get("code")
        if not isinstance(code, str) or not code:
            raise ToolProviderOAuthError("KontoCSV authorization code is missing.")
        state = request.args.get("state")
        if not isinstance(state, str) or len(state) > 1024:
            raise ToolProviderOAuthError("KontoCSV authorization state is invalid.")
        try:
            verifier = _cipher(redirect_uri, system_credentials).decrypt(state.encode("ascii"), ttl=600).decode("ascii")
        except (InvalidToken, UnicodeError, ValueError) as exc:
            raise ToolProviderOAuthError("KontoCSV OAuth state expired or failed verification.") from exc
        return _exchange_token({
            "grant_type": "authorization_code",
            "code": code, "redirect_uri": redirect_uri,
            "resource": RESOURCE_URL, "code_verifier": verifier,
        }, system_credentials)

    def _oauth_refresh_credentials(
        self, redirect_uri: str, system_credentials: Mapping[str, Any],
        credentials: Mapping[str, Any]
    ) -> ToolOAuthCredentials:
        refresh = credentials.get("refresh_token")
        if not isinstance(refresh, str) or not refresh:
            raise ToolProviderOAuthError("Reconnect KontoCSV to restore access.")
        updated = _exchange_token({
            "grant_type": "refresh_token",
            "refresh_token": refresh,
            "resource": RESOURCE_URL,
        }, system_credentials)
        if "refresh_token" not in updated.credentials:
            return ToolOAuthCredentials(
                credentials={**updated.credentials, "refresh_token": refresh},
                expires_at=updated.expires_at,
            )
        return updated
