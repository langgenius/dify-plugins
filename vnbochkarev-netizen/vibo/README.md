# ViBo Memory — Dify plugin

Persistent encrypted memory (L1/L2/L3) for Dify agents.

## Features
- **memory_search** — recall relevant facts (97.5% fewer tokens than full history)
- **memory_add** — save facts (L1 public / L2 private / L3 secrets)
- **thread_memory** — conversation context across sessions
- **usage** — token savings report

## Setup
1. Get a free trial key: https://wwwvibo.com (2 days, no card)
2. Install this plugin in Dify (Plugin Marketplace or local install)
3. Enter your ViBo key in plugin credentials

## Pricing
From $2.5/month (launch offer, first 100 users). https://wwwvibo.com

## Security
- AES-256-GCM encryption, per-key isolation
- **L3 secrets never reach the LLM** — the model cannot leak what it never saw
- Local-first: your memory file stays on your machine

Docs: https://github.com/vnbochkarev-netizen/ViBo-memory
