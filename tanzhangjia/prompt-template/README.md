# Prompt Template — Dify Plugin

The simplest kind. A **variable replacer**.

Just like the LLM node prompt editor: two input boxes (system prompt template + user prompt template) where you write `{{variable}}` placeholders. The plugin substitutes them with real values and outputs the rendered string.

- **Source repository**: [github.com/tanzhangjia/prompt-template](https://github.com/tanzhangjia/prompt-template)
- **License**: MIT

## What it does

| Feature | Description |
|---|---|
| Inputs | System prompt template, user prompt template, optional extra variables |
| Outputs | `system_prompt`, `user_prompt`, or a single `prompt` string |
| Logic | Pure placeholder substitution with Python standard library `re` |
| Dependencies | None beyond the Dify plugin SDK |

It is **not** a Jinja engine. No loops, no conditionals, no filters — just `{{variable}}` replacement, matching the mental model of the Dify prompt editor.

## Installation

```bash
# From the plugin source directory
dify plugin install prompt-template/
```

Or install the packaged `.difypkg` via the Dify plugin management UI / CLI.

## Usage

### Simple: replace the LLM node system prompt

1. Add a **Prompt Template** node to your workflow.
2. In **system prompt template**, write:

```
You are a translation assistant.
Today's date is {{nodes.date.current}}.
Target language: {{nodes.input.lang}}
```

3. Pass the rendered `prompt` output to the LLM node system prompt.

### Full: system + user prompt

1. **System prompt template**: write the system-level prompt.
2. **User prompt template**: write the user-level prompt, for example:

```
Answer based on the information below.

Background: {{nodes.search.output}}

User question: {{nodes.input.text}}
```

3. Use the `system_prompt` and `user_prompt` outputs respectively.

### Extra variables

If a variable is not selectable from the Dify variable panel (for example a nested property of a node), pass it in as a key-value pair in **extra variables**.

## Output

### Dual-output mode (default)

| Output | Meaning |
|---|---|
| `system_prompt` | Rendered system prompt template |
| `user_prompt` | Rendered user prompt template |

### Single-output mode (`system_only=true`)

| Output | Meaning |
|---|---|
| `prompt` | Rendered result of `system_template` only |

## Credentials & connection

The plugin requires **no credentials** and makes **no network connections**. `storage`, `endpoint`, `tool`, and `model` permissions are all disabled in `manifest.yaml`. Everything runs in-memory as a pure string transformation.

## Security

- No network requests, no file operations, no external services.
- No template injection risk: the plugin only replaces `{{variable}}` placeholders and does not evaluate expressions.

## Why not Jinja?

1. **Consistent with Dify's mental model** — the prompt editor and variable panel already use `{{variable}}` syntax, so users do not need to learn another template syntax.
2. **Safer** — Jinja's `{% ... %}` can execute arbitrary expressions and carries template-injection risk with untrusted input. This plugin is immune by design.
3. **Lighter** — no Jinja2 dependency; smaller runtime and package size.
4. **Right fit** — prompt stitching rarely needs loops or branches; if logic is required, use a Code node or a workflow conditional instead.

**When do you need Jinja?** If you need loops, conditionals, filters, macros, or generating non-prompt structured documents, use Jinja (or Dify's built-in Code node). This plugin is the minimal solution for "pure concatenation".

## Localized README

A Chinese version is available in `README.zh_Hans.md`.
