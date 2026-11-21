from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from weydub_api import ApiError, call


class WeydubProvider(ToolProvider):
    def _validate_credentials(self, credentials):
        try:
            call(credentials, "point/query", {"notZero": True, "isValid": True})
        except ApiError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from None
