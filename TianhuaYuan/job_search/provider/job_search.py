from __future__ import annotations

from typing import Any

from dify_plugin import ToolProvider


class JobSearchProvider(ToolProvider):
    """Provider for job_search. Uses free, key-less public APIs, so there
    are no credentials to validate.
    """

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # The public job board APIs need no credentials, so there is nothing
        # to validate. The default base implementation would raise, so we
        # override it to a no-op.
        return
