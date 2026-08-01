# PayPack Value Evaluator — Dify Plugin

> AI服务价值评估工具 — 帮助AI代理在支付前做出更聪明的决策。

## Important: This plugin does NOT handle payments

This plugin evaluates whether a payment is **worth making**, but it does NOT
execute any payment itself. Think of it as a "credit check" or "risk assessment"
tool — it tells you if you should proceed, but the actual payment must be done
by a separate tool (such as PayPack Payment Tool).

## How it works

```
1. FetchServiceMetadata  →  reads a public JSON file from the service provider
2. EvaluatePayment        →  compares the metadata against your budget and risk settings
3. (Your payment tool)    →  executes the actual payment if approved
```

## Tools

### fetch_service_metadata

Fetches the AI service metadata from a given base URL via `/.well-known/ai-service-metadata.json`.

**Input:** `service_url` (e.g., `https://api.weather.com`)

**Output:** Structured metadata including pricing, performance, reputation, and policy.

### evaluate_payment

Evaluates whether to proceed with payment based on the metadata.

**Input:**
- `metadata` — from fetch_service_metadata
- `budget` — max budget
- `min_trust_score` — default 80
- `min_success_rate` — default 0.95

**Output:** `APPROVE` or `REJECT` with detailed check results.

## License

Apache 2.0
