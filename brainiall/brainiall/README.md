# Brainiall LLM Gateway

Access 113+ AI models from 17 providers through a single OpenAI-compatible API, powered by AWS Bedrock.

## Available Models

| Model | Context | Pricing ($/MTok) |
|-------|---------|-------------------|
| Claude Opus 4.6 | 200K | $5 / $25 |
| Claude Sonnet 4.6 | 200K | $3 / $15 |
| Claude Haiku 4.5 | 200K | $1 / $5 |
| Claude Opus 4.5 | 200K | $15 / $75 |
| DeepSeek R1 | 128K | $1.35 / $5.40 |
| DeepSeek V3 | 128K | $0.27 / $1.10 |
| Llama 3.3 70B | 128K | $0.72 / $0.72 |
| Llama 4 Scout 17B | 512K | $0.17 / $0.17 |
| Qwen 3 235B | 128K | $0.80 / $2.40 |
| Mistral Large 3 | 128K | $2 / $6 |
| Amazon Nova Pro | 300K | $0.80 / $3.20 |
| Amazon Nova Micro | 128K | $0.035 / $0.14 |

Plus 100+ additional models available as custom models.

## Setup

1. Get your API key from [brainiall.com](https://brainiall.com)
2. Install this plugin in your Dify instance
3. Go to **Settings > Model Providers** and find **Brainiall**
4. Enter your API key and click **Save**

## Custom Models

You can also add any of the 113+ models not listed as predefined by using the **Add Model** option. Enter the model name exactly as listed in the API catalog and configure context size, max tokens, and function calling support.

Full model catalog: https://brainiall.com

## Features

- OpenAI-compatible API endpoint
- Streaming responses
- Function calling / tool use support
- Vision support (Claude, Nova Pro, Mistral Large 3, Llama 4 Scout)
- Competitive pricing via AWS Bedrock

## Contact

- Website: https://brainiall.com
- Email: fasuizu@brainiall.com
- Repository: https://github.com/fasuizu-br/dify-brainiall-plugin
