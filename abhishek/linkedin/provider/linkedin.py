from typing import Any, Mapping
import urllib.parse
import requests
import time

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin.entities.oauth import ToolOAuthCredentials


class LinkedinProvider(ToolProvider):
    
    def _validate_credentials(self, credentials: Mapping[str, Any]) -> None:
        if not credentials.get("access_token"):
            raise ToolProviderCredentialValidationError("Access token is missing")

    def _oauth_get_authorization_url(self, redirect_uri: str, system_credentials: Mapping[str, Any]) -> str:
        """
        Generate the authorization URL for LinkedIn OAuth.
        """
        client_id = system_credentials.get("client_id")
        if not client_id:
            raise ToolProviderCredentialValidationError("Client ID is required")
            
        # Define scopes
        # w_member_social is standard for posting to personal profiles.
        # w_organization_social and r_organization_social are needed for organization pages.
        # openid, profile, email are standard for identity.
        scopes = ["w_member_social", "w_organization_social", "r_organization_social", "openid", "profile", "email"]
        scope_str = " ".join(scopes)
        
        params = {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope_str,
        }
        
        base_url = "https://www.linkedin.com/oauth/v2/authorization"
        # Using quote_via to ensure spaces are encoded as %20
        return f"{base_url}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote)}"
        
    def _oauth_get_credentials(
        self, redirect_uri: str, system_credentials: Mapping[str, Any], request: Any
    ) -> ToolOAuthCredentials:
        """
        Exchange code for access_token.
        """
        code = request.args.get("code")
        
        # Check for error in callback
        error = request.args.get("error")
        if error:
            error_desc = request.args.get("error_description", "Unknown error")
            raise ToolProviderCredentialValidationError(f"LinkedIn Auth Error: {error} - {error_desc}")

        if not code:
            raise ToolProviderCredentialValidationError("Authorization code not found in request")
            
        client_id = system_credentials.get("client_id")
        client_secret = system_credentials.get("client_secret")
        
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            
            # Calculate expires_at
            expires_in = token_data.get("expires_in", -1)
            expires_at = int(time.time()) + expires_in if expires_in > 0 else -1

            return ToolOAuthCredentials(
                credentials={
                    "access_token": token_data.get("access_token"),
                    "expires_in": expires_in,
                    "refresh_token": token_data.get("refresh_token")
                },
                expires_at=expires_at
            )
        except requests.exceptions.HTTPError as e:
             raise ToolProviderCredentialValidationError(f"Token Exchange Failed: {str(e)} - Response: {e.response.text}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Failed to exchange token: {str(e)}")
            
    def _oauth_refresh_credentials(
            self, redirect_uri: str, system_credentials: Mapping[str, Any], credentials: Mapping[str, Any]
        ) -> ToolOAuthCredentials:
        # LinkedIn tokens typically last 60 days.
        # For now, return existing wrapped in ToolOAuthCredentials.
        return ToolOAuthCredentials(
            credentials=credentials,
            expires_at=int(time.time()) + int(credentials.get("expires_in", 0)) if credentials.get("expires_in") else -1
        )
