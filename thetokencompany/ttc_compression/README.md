# TTC Compression - Dify Plugin

LLM input compression middleware by **The Token Company**. This plugin provides a tool that compresses text to reduce token usage before sending to any LLM.

## Features

- **Model Agnostic**: Works with any LLM - use it in workflows before any model node
- **Simple Integration**: Just a single tool that takes text in and outputs compressed text
- **Configurable Compression**: Adjust aggressiveness from light (0.2) to aggressive (0.7)
- **JSON Protection**: Optionally preserve JSON structures during compression
- **Compression Stats**: Returns token counts and savings metrics

## Setup

### Prerequisites

1. A Token Company API key from [thetokencompany.com/dashboard](https://thetokencompany.com/dashboard)

### Configuration

1. Install the plugin in your Dify instance
2. Navigate to **Tools** in your workspace
3. Find "TTC Compression" and click **Authorize**
4. Enter your TTC API key

## Usage

### In Workflows

Add the **Compress Text** tool node before your LLM node:

1. Add a "Compress Text" tool node
2. Connect your input text to the `text` parameter
3. Set compression level and JSON protection as needed
4. Connect the output to your LLM node's input

### Tool Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `text` | string | Yes | - | The text to compress |
| `aggressiveness` | select | No | 0.5 | Compression level (0.2, 0.5, or 0.7) |
| `protect_json` | boolean | No | true | Preserve JSON structures |

### Output

The tool returns:
- **Text output**: The compressed text (use this as input to your LLM)
- **JSON output**: Compression statistics including:
  - `compressed_text`: The compressed result
  - `original_tokens`: Token count before compression
  - `output_tokens`: Token count after compression
  - `tokens_saved`: Number of tokens saved
  - `compression_ratio`: Output/input ratio
  - `compression_time_seconds`: Processing time

## Compression Levels

| Level | Aggressiveness | Use Case |
|-------|----------------|----------|
| Light | 0.2 | Minimal compression, highest quality |
| Moderate | 0.5 | Balanced compression and quality |
| Aggressive | 0.7 | Maximum token savings |

## Example Workflow

```
[User Input] → [Compress Text Tool] → [LLM Node] → [Output]
```

The compressed text maintains semantic meaning while using fewer tokens, reducing costs when sent to any LLM provider.

## Cost Savings

Typical compression ratios:
- Light: 10-20% token reduction
- Moderate: 25-40% token reduction
- Aggressive: 40-60% token reduction

Your actual savings depend on the content being compressed.

## Privacy & Security

- All compression happens via secure HTTPS connections
- API keys are stored securely using Dify's credential management
- Text is processed by The Token Company API - see privacy policy for details

## Support

- Documentation: [thetokencompany.com/docs](https://thetokencompany.com/docs)
- Issues: Report bugs via GitHub or email support@thetokencompany.com

## License

MIT License
