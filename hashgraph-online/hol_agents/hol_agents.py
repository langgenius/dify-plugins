"""
HOL Agents - Dify Tool Plugin

Discover and interact with AI agents on the Hashgraph Online registry.
"""

import httpx
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


HOL_REGISTRY_BASE = "https://hol.org/registry/api/v1"


class SearchAgentsTool(Tool):
    """Search for AI agents in the HOL registry."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> list[ToolInvokeMessage]:
        query = tool_parameters.get("query", "")
        limit = tool_parameters.get("limit", 10)

        if not query:
            return [self.create_text_message("Error: query parameter is required")]

        url = f"{HOL_REGISTRY_BASE}/search?q={query}&limit={limit}"

        try:
            with httpx.Client() as client:
                response = client.get(url, timeout=30.0)
                response.raise_for_status()
                data = response.json()

            hits = data.get("hits", [])
            total = data.get("total", 0)

            result_lines = [f"Found {total} agents matching '{query}':\n"]

            for i, agent in enumerate(hits[:limit], 1):
                name = agent.get("name", "Unknown")
                uaid = agent.get("uaid", "")
                trust_score = agent.get("trustScore", "N/A")
                description = agent.get("description", "")[:200]
                capabilities = agent.get("capabilities", [])

                result_lines.append(f"{i}. **{name}**")
                result_lines.append(f"   UAID: {uaid}")
                result_lines.append(f"   Trust Score: {trust_score}")
                if description:
                    result_lines.append(f"   Description: {description}...")
                if capabilities:
                    result_lines.append(f"   Capabilities: {', '.join(capabilities[:5])}")
                result_lines.append("")

            return [self.create_text_message("\n".join(result_lines))]

        except httpx.HTTPError as e:
            return [self.create_text_message(f"HTTP Error: {str(e)}")]
        except Exception as e:
            return [self.create_text_message(f"Error: {str(e)}")]


class GetAgentTool(Tool):
    """Get detailed information about a specific agent."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> list[ToolInvokeMessage]:
        uaid = tool_parameters.get("uaid", "")

        if not uaid:
            return [self.create_text_message("Error: uaid parameter is required")]

        # Format UAID if needed
        if not uaid.startswith("uaid:"):
            uaid = f"uaid:{uaid}"

        url = f"{HOL_REGISTRY_BASE}/agents/{uaid}"

        try:
            with httpx.Client() as client:
                response = client.get(url, timeout=30.0)
                response.raise_for_status()
                agent = response.json()

            name = agent.get("name", "Unknown")
            trust_score = agent.get("trustScore", "N/A")
            description = agent.get("description", "No description available")
            capabilities = agent.get("capabilities", [])
            protocols = agent.get("protocols", [])
            registry = agent.get("registry", "Unknown")

            result_lines = [
                f"## {name}",
                f"**UAID:** {uaid}",
                f"**Registry:** {registry}",
                f"**Trust Score:** {trust_score}",
                "",
                f"**Description:** {description}",
            ]

            if capabilities:
                result_lines.append("\n**Capabilities:**")
                for cap in capabilities:
                    result_lines.append(f"- {cap}")

            if protocols:
                result_lines.append("\n**Protocols:**")
                for proto in protocols:
                    result_lines.append(f"- {proto}")

            return [self.create_text_message("\n".join(result_lines))]

        except httpx.HTTPError as e:
            return [self.create_text_message(f"HTTP Error: {str(e)}")]
        except Exception as e:
            return [self.create_text_message(f"Error: {str(e)}")]


class SimilarAgentsTool(Tool):
    """Find agents similar to a given agent."""

    def _invoke(self, tool_parameters: dict[str, Any]) -> list[ToolInvokeMessage]:
        uaid = tool_parameters.get("uaid", "")

        if not uaid:
            return [self.create_text_message("Error: uaid parameter is required")]

        # Format UAID if needed
        if not uaid.startswith("uaid:"):
            uaid = f"uaid:{uaid}"

        url = f"{HOL_REGISTRY_BASE}/agents/{uaid}/similar"

        try:
            with httpx.Client() as client:
                response = client.get(url, timeout=30.0)
                response.raise_for_status()
                data = response.json()

            similar = data.get("similar", data.get("hits", []))

            if not similar:
                return [self.create_text_message("No similar agents found.")]

            result_lines = ["## Similar Agents\n"]

            for i, agent in enumerate(similar, 1):
                name = agent.get("name", "Unknown")
                agent_uaid = agent.get("uaid", "")
                trust_score = agent.get("trustScore", "N/A")

                result_lines.append(f"{i}. **{name}** (Trust: {trust_score})")
                result_lines.append(f"   UAID: {agent_uaid}")

            return [self.create_text_message("\n".join(result_lines))]

        except httpx.HTTPError as e:
            return [self.create_text_message(f"HTTP Error: {str(e)}")]
        except Exception as e:
            return [self.create_text_message(f"Error: {str(e)}")]
