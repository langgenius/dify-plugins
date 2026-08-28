# Tool-Capture Agent — Dify Plugin

Author: **gitpoldan**. Version: **0.3.3**. Requires Dify **>= 1.16.1**.

Agent-strategy plugin extending Dify's Function-Calling agent. Same model, tools,
instruction, and iterations as the stock agent, plus:

- **Capture** — every tool call exposed as workflow variables (`tool_calls`, `tool_outputs`, `mapped_outputs`, ...)
- **I/O wiring** — JSON `io_wiring` links outputs to inputs via runtime indexes (large payloads bypass LLM context)
- **Incoming files** — wire `files` to `{{#sys.files#}}` for multimodal Chatflow attachments
- **Skills & Tools routing** — optional YAML catalogs for a compact system prompt and focused tool set

Provider id: `gitpoldan/tool_capture_agent`. Strategy: **Function Calling (Tool-Capture)**.

## Setup

1. Install the plugin in Dify.
2. Add an **Agent** node; select strategy **Tool-Capture Agent → Function Calling**.
3. Configure like a normal agent: Model, Tools, Instruction, Query, Max Iterations.
4. (Optional) Set **Files** to `{{#sys.files#}}` for Chatflow attachments (vision model for images).
5. (Optional) **I/O wiring (JSON)** and **Output mappings (JSON)** for advanced workflows.
6. (Optional) **Skills catalog (YAML)** / **Tools catalog (YAML)** for routing.

No plugin-specific credentials. Uses LLM and tools already configured in the node.

## Usage

Downstream nodes can reference captured outputs:

```
Weather: {{#agent.mapped_outputs.weather#}}
Total tool calls: {{#agent.tool_calls_count#}}
```

Key output variables: `text`, `final_answer`, `tool_calls`, `tool_outputs`,
`last_tool_outputs`, `mapped_outputs`, `captured_files`, `skills_tools_routing`.

For tool-generated file download cards in chat, use `{{#agent.files#}}` in an Answer node.

Extended documentation (I/O wiring, Skills routing, output mappings) is in the
[source repository](https://github.com/gitpoldan/dify/tree/main/polden-plugins/tool_capture_agent).

## Privacy

Captured outputs exist only for one Agent execution. See [PRIVACY.md](PRIVACY.md).

## Support

- Source: https://github.com/gitpoldan/dify/tree/main/polden-plugins/tool_capture_agent
- GitHub Issues: https://github.com/gitpoldan/dify/issues
- Email: bv2020donch@gmail.com

Russian documentation: [readme/README_ru_RU.md](readme/README_ru_RU.md).
