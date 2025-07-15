import os
import httpx
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Plugin, DifyPluginEnv

if __name__ == "__main__":
    plugin = Plugin(DifyPluginEnv())
    plugin.run()