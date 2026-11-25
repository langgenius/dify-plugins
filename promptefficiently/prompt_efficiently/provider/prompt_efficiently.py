from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.pe_api import PEError, send_code  # noqa: E402


class PromptEfficientlyProvider(ToolProvider):
    """Two-step email-code sign-in, same as every other Prompt Efficiently tool.

    First save (empty code field): a 6-digit code is emailed and validation fails
    on purpose with instructions. Second save (code filled in): the code's format
    is checked and the credentials are stored; the code is exchanged for a session
    token on first use, so a wrong or expired code surfaces as a clear tool error.
    """

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        email = (credentials.get("pe_email") or "").strip().lower()
        code = (credentials.get("pe_code") or "").strip()
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            raise ToolProviderCredentialValidationError("Enter the email for your Prompt Efficiently account.")
        if not code:
            try:
                send_code(email)
            except PEError as e:
                raise ToolProviderCredentialValidationError(str(e))
            raise ToolProviderCredentialValidationError(
                "A 6-digit sign-in code is on its way to %s. Paste it into the Sign-in code field and save again." % email
            )
        if not (len(code) == 6 and code.isdigit()):
            raise ToolProviderCredentialValidationError("The sign-in code is six digits.")
