"""Edict IQ OAuth 2.0 provider. OAuth credentials are supplied by Dify, never in source."""
from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlencode

import requests
from dify_plugin import ToolProvider
from dify_plugin.entities.oauth import ToolOAuthCredentials
from dify_plugin.errors.tool import ToolProviderCredentialValidationError, ToolProviderOAuthError
from tools.mcp_client import call_mcp, EdictIqMcpError

AUTH_URL = "https://vweumwphoufbatnalcte.supabase.co/auth/v1/oauth/authorize"
TOKEN_URL = "https://vweumwphoufbatnalcte.supabase.co/auth/v1/oauth/token"
RESOURCE_URL = "https://edictiq.com/api/mcp"
SCOPES = "openid email offline_access"


def _exchange_token(data: dict[str, str], creds: Mapping[str, Any]) -> ToolOAuthCredentials:
    client_id, client_secret = creds.get("client_id"), creds.get("client_secret")
    if not client_id or not client_secret:
        raise ToolProviderOAuthError("Configure the Edict IQ OAuth client first.")
    try:
        response = requests.post(TOKEN_URL, data=data, auth=(str(client_id), str(client_secret)),
                                 timeout=(5, 15), allow_redirects=False)
    except requests.RequestException as exc:
        raise ToolProviderOAuthError("Edict IQ OAuth token endpoint unavailable.") from exc
    if response.status_code != 200:
        raise ToolProviderOAuthError("Edict IQ OAuth token exchange was rejected.")
    try:
        token = response.json()
    except ValueError as exc:
        raise ToolProviderOAuthError("Edict IQ OAuth token response is invalid.") from exc
    if not isinstance(token, dict) or not isinstance(token.get("access_token"), str):
        raise ToolProviderOAuthError("Edict IQ did not return an OAuth access token.")
    result = {"access_token": token["access_token"]}
    if isinstance(token.get("refresh_token"), str):
        result["refresh_token"] = token["refresh_token"]
    try:
        expires_at = int(time.time()) + max(60, int(token.get("expires_in", 3600)))
    except (TypeError, ValueError) as exc:
        raise ToolProviderOAuthError("Edict IQ returned an invalid token lifetime.") from exc
    return ToolOAuthCredentials(credentials=result, expires_at=expires_at)


class EdictIqProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        token = credentials.get("access_token")
        if not token:
            raise ToolProviderCredentialValidationError("Connect Edict IQ through OAuth.")
        try:
            call_mcp("list_connected_workspaces", {}, token)
        except EdictIqMcpError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from exc

    def _oauth_get_authorization_url(self, redirect_uri: str, system_credentials: Mapping[str, Any]) -> str:
        if not system_credentials.get("client_id") or not system_credentials.get("client_secret"):
            raise ToolProviderOAuthError("Set up the Edict IQ OAuth client ID and secret.")
        if not isinstance(redirect_uri, str) or not redirect_uri.startswith("https://"):
            raise ToolProviderOAuthError("Dify must provide a secure OAuth callback.")
        params = {"client_id": str(system_credentials["client_id"]), "redirect_uri": redirect_uri,
                  "response_type": "code", "scope": SCOPES, "resource": RESOURCE_URL}
        return AUTH_URL + "?" + urlencode(params)

    def _oauth_get_credentials(self, redirect_uri: str, system_credentials: Mapping[str, Any], request: Any) -> ToolOAuthCredentials:
        if request.args.get("error"):
            raise ToolProviderOAuthError("Edict IQ authorization was not approved.")
        code = request.args.get("code")
        if not isinstance(code, str) or not code:
            raise ToolProviderOAuthError("Edict IQ authorization code is missing.")
        return _exchange_token(
            {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri,
             "resource": RESOURCE_URL},
            system_credentials,
        )

    def _oauth_refresh_credentials(
        self, redirect_uri: str, system_credentials: Mapping[str, Any], credentials: Mapping[str, Any]
    ) -> ToolOAuthCredentials:
        refresh = credentials.get("refresh_token")
        if not isinstance(refresh, str) or not refresh:
            raise ToolProviderOAuthError("Reconnect Edict IQ to restore access.")
        updated = _exchange_token(
            {"grant_type": "refresh_token", "refresh_token": refresh, "resource": RESOURCE_URL},
            system_credentials,
        )
        if "refresh_token" not in updated.credentials:
            return ToolOAuthCredentials(
                credentials={**updated.credentials, "refresh_token": refresh},
                expires_at=updated.expires_at,
            )
        return updated
