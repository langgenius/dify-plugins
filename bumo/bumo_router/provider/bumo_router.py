import logging

from dify_plugin import ModelProvider
from dify_plugin.errors.model import CredentialsValidateFailedError

from models.router_client import RouterKeyError, check_key

logger = logging.getLogger(__name__)


class BumoRouterProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: dict) -> None:
        """只验 Key（自动识别国内站 / 国际站），不发真实对话，不花钱。"""
        try:
            check_key(credentials.get("api_key", ""), credentials.get("endpoint_url") or None)
        except RouterKeyError as e:
            raise CredentialsValidateFailedError(str(e)) from e
        except Exception as e:
            logger.exception("bumo_router credentials validate failed")
            raise CredentialsValidateFailedError(f"连接 Router 失败 / Failed to reach Router: {e}") from e
