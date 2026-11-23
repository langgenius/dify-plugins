import logging

from dify_plugin import ModelProvider
from dify_plugin.entities.model import ModelType
from dify_plugin.errors.model import CredentialsValidateFailedError

logger = logging.getLogger(__name__)


class FikraProvider(ModelProvider):
    # Cheapest chat model in the catalog keeps credential checks near-free.
    _VALIDATION_MODEL = "qwen3.8-27b"

    def validate_provider_credentials(self, credentials: dict) -> None:
        try:
            self.get_model_instance(ModelType.LLM).validate_credentials(
                model=self._VALIDATION_MODEL, credentials=credentials
            )
        except CredentialsValidateFailedError:
            raise
        except Exception as ex:
            logger.exception("fikra credentials validation failed")
            raise CredentialsValidateFailedError(str(ex)) from ex
