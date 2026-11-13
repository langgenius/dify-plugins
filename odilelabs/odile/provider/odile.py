from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools._client import OdileDirectClient


class OdileProvider(ToolProvider):
    def _validate_credentials(self, credentials):
        try:
            OdileDirectClient().call("get_m2m_network", {})
        except Exception as error:
            raise ToolProviderCredentialValidationError(str(error)) from error
