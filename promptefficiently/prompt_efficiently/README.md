# Prompt Efficiently for Dify

Estimate what a prompt will cost on an AI product **before** you send it, and get a shorter rewrite that aims to do the same job for less - inside any Dify Chatflow, Workflow or Agent.

- **Estimate prompt cost**: rough usage estimate (messages, credits, tokens or dollars) for ChatGPT, Claude, Gemini, Grok, Town AI, Manus, Lovable, Bolt and Replit, with a fits / tight / over verdict against the plan's allowance and the cheapest free alternative. The maths runs inside this plugin; **your prompt text is never sent to Prompt Efficiently for an estimate.**
- **Prompt Efficiently rewrite**: sends the prompt to Prompt Efficiently's live rewrite service (only when you turn on the 18+ consent in the plugin settings) and returns a shorter version to review. Modes: shorter, clearer, more specific.

Estimates are rough guides, not quotes, bills or balance readings.

## Requirements

A Prompt Efficiently account. Free accounts include 5 estimates a day and 5 AI rewrites; Pro (£9.99/month or £99/year) is unlimited estimates and more rewrites. Sign up at https://promptefficiently.com/app - email sign-in, no passwords.

## Setup

1. Install the plugin and open its settings.
2. Enter your Prompt Efficiently account email. Leave the sign-in code field **empty** and save. Saving will report an error on purpose: a 6-digit code is now on its way to your email.
3. Paste the code into the sign-in code field and save again. The plugin exchanges it for a session on first use and keeps the session in Dify's plugin storage.
4. Optional, only for the rewrite tool: tick the 18+ consent agreeing that text sent to the rewrite tool is processed by Prompt Efficiently and its AI provider, then save.

Codes expire after 10 minutes. If a session expires later, repeat steps 2-3.

## Usage

### Estimate prompt cost

| Parameter | Required | Notes |
| --- | --- | --- |
| prompt | yes | The full prompt text. |
| platform | yes | chatgpt, claude, gemini, grok, town, manus, lovable, bolt or replit. |
| size | no | small, medium (default) or big. |
| plan | no | Paid plan id on that product, e.g. plus, pro, max, starter, core. Empty = free plan. |

Returns the estimated range, verdict, rough input-token count, the plan's allowance context, a cheapest free alternative where one exists, and how many free estimates remain today. Each call counts as one estimate toward the account's allowance (Free: 5 a day; Pro: unlimited).

### Prompt Efficiently rewrite

| Parameter | Required | Notes |
| --- | --- | --- |
| text | yes | The prompt to rewrite. Sent to Prompt Efficiently and its AI provider. |
| mode | no | shorter (default), clearer or more_specific. |

Returns the rewrite with a review warning. Meaning preservation and lower costs are not guaranteed; review against your original.

A handy agent pattern: estimate, rewrite, estimate again, and show the saving.

## Privacy

See [PRIVACY.md](PRIVACY.md) and https://promptefficiently.com/privacy.

## Source and contact

- Source: https://github.com/promptefficiently/dify-plugin-prompt-efficiently
- Website: https://promptefficiently.com
- Contact: promptefficiently@gmail.com

Prompt Efficiently is not affiliated with, endorsed by or sponsored by any AI company it estimates. Logos and names belong to their owners.
