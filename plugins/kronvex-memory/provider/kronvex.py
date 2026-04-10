from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import httpx


class KronvexProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        base_url = credentials.get("base_url", "https://api.kronvex.io").rstrip("/")
        api_key = credentials.get("api_key", "")
        try:
            resp = httpx.get(
                f"{base_url}/health",
                headers={"X-API-Key": api_key},
                timeout=10,
            )
            resp.raise_for_status()
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
