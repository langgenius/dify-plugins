# OraClaw -- Decision Intelligence for Dify

Add real mathematical optimization to your Dify workflows. 5 algorithm tools, all under 25ms.

## Tools

| Tool | What It Does |
|------|-------------|
| **Multi-Armed Bandit** | Select the best option (UCB1/Thompson/epsilon-Greedy) |
| **LP/MIP Solver** | Budget allocation, scheduling, constraint satisfaction |
| **Graph Analytics** | PageRank, communities, shortest path |
| **Anomaly Detection** | Z-score/IQR outlier detection |
| **Time Series Forecast** | ARIMA/Holt-Winters with confidence intervals |

## Setup

1. Get a free API key: `curl -X POST https://oraclaw-api.onrender.com/api/v1/auth/signup -H "Content-Type: application/json" -d '{"email":"you@example.com"}'`
2. Install the OraClaw plugin in your Dify instance
3. Enter your API key in the plugin settings
4. Use the tools in your Dify workflows

## Pricing

- **Free signup**: 1,000 calls/day at $0.005/call (metered)
- **Starter**: $9/mo for 50,000 calls
- **Growth**: $49/mo for 500,000 calls

## Links

- [GitHub](https://github.com/Whatsonyourmind/oraclaw)
- [npm MCP Server](https://www.npmjs.com/package/@oraclaw/mcp-server)
- [API Documentation](https://oraclaw-api.onrender.com/api/v1/pricing)
