import logging
from collections.abc import Mapping

from dify_plugin import ModelProvider
from dify_plugin.errors.model import CredentialsValidateFailedError

logger = logging.getLogger(__name__)


class BrainiallModelProvider(ModelProvider):
    def validate_provider_credentials(self, credentials: Mapping) -> None:
        """
        Validate provider credentials.
        If validation fails, raise CredentialsValidateFailedError.
        """
        try:
            model_instance = self.get_model_instance("llm")
            model_instance.validate_credentials(
                model="deepseek-v3",
                credentials={
                    "brainiall_api_key": credentials["brainiall_api_key"],
                    "mode": "chat",
                },
            )
        except CredentialsValidateFailedError as ex:
            raise ex
        except Exception as ex:
            logger.exception(
                f"{self.get_provider_schema().provider} credentials validate failed"
            )
            raise ex
