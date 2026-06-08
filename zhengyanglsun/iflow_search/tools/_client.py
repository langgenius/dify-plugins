"""Shared iFlow Search client builder for all three Dify tools.

Centralizes:

* Attribution stamping (``source="dify"`` + integration name/version) so the
  iFlow side sees consistent ``IFlow-Source`` / ``IFlow-Integration-Name`` /
  ``IFlow-Integration-Version`` headers from this plugin.
* The plugin version string used as ``integration_version``. Bump
  :data:`PLUGIN_VERSION` together with ``manifest.yaml``'s ``version`` and
  ``meta.version`` when releasing.

The API key is passed in by argument and never logged here. Construction
errors raised by the SDK (e.g. missing key) propagate untouched — callers map
them via :mod:`tools._errors`.
"""

from __future__ import annotations

from iflow_search import IFlowSearchClient

PLUGIN_VERSION = "0.0.1"
ATTRIBUTION_SOURCE = "dify"
ATTRIBUTION_INTEGRATION_NAME = "iflow-search-dify"


def build_client(*, api_key: str) -> IFlowSearchClient:
    """Construct a sync iFlow Search client with consistent attribution.

    Returned as a context manager so callers do ``with build_client(...) as c:``.
    """
    return IFlowSearchClient(
        api_key=api_key,
        source=ATTRIBUTION_SOURCE,
        integration_name=ATTRIBUTION_INTEGRATION_NAME,
        integration_version=PLUGIN_VERSION,
    )
