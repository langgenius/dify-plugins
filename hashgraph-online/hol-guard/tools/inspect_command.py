from collections.abc import Generator
from pathlib import Path
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class InspectCommandTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        from codex_plugin_scanner.guard.runtime.command_inspection import inspect_command

        command = str(tool_parameters.get("command") or "").strip()
        if not command:
            raise ValueError("command cannot be empty")

        result = inspect_command(
            command,
            cwd=Path.cwd(),
            home_dir=Path.home(),
        )
        result["mode"] = "test"
        yield self.create_json_message(result)
