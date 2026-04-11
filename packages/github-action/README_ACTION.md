# SupraWall Security Scan 🛡️

**The deterministic security layer for AI agents.**

SupraWall Security Scan detects credential leaks, hardcoded secrets, and unsafe execution patterns in your AI agent code before they reach production. It enforces runtime security policies and helps you comply with the EU AI Act (Article 9, 13, and 14).

[![Marketplace](https://img.shields.io/badge/GitHub-Marketplace-blue.svg)](https://github.com/marketplace/actions/suprawall-security-scan)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](LICENSE)
[![Website](https://img.shields.io/badge/Website-supra--wall.com-lightgrey)](https://www.supra-wall.com)

---

## 🚀 Quick Start

Add the following to your GitHub Actions workflow (e.g., `.github/workflows/security.yml`):

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: SupraWall Scan
        uses: wiserautomation/SupraWall@v1
        with:
          api-key: ${{ secrets.SUPRAWALL_API_KEY }}
          agent-path: './agents' # Directory containing your agent code
          fail-on: 'high'        # Fail the build on high/critical violations
```

---

## 🛡️ Why SupraWall?

Standard static analysis tools aren't built for the unique risks of AI agents. SupraWall is:

- **Deterministic**: Blocks known attack patterns (SQLi, XSS, Prompt Injection) with zero network calls.
- **Framework Aware**: Native detection for LangChain, CrewAI, AutoGen, and Vercel AI SDK.
- **Compliance First**: Generates audit trails required for EU AI Act readiness.
- **Zero Friction**: One line of config to secure your entire pipeline.

---

## 🔑 Getting an API Key

1. Visit [supra-wall.com/signup](https://www.supra-wall.com/signup) and create a free account.
2. Go to **Settings > API Keys** and generate a new key.
3. Add the key to your GitHub repository secrets as `SUPRAWALL_API_KEY`.

---

## 📊 Feature Comparison

| Feature | SupraWall | Lakera | Guardrails AI |
|---------|-----------|--------|---------------|
| **Secret Detection** | ✅ | ✅ | ✅ |
| **Prompt Injection** | ✅ | ✅ | ❌ |
| **Framework Detection** | ✅ | ❌ | ❌ |
| **Runtime Protection** | ✅ | ❌ | ✅ |
| **EU AI Act Audit** | ✅ | ❌ | ❌ |

---

## 📄 Documentation

For full configuration options and policy examples, visit [docs.supra-wall.com](https://www.supra-wall.com/docs).

---

## 💬 Community

Join our [Discord Community](https://discord.gg/suprawall) for support, feature requests, and security discussions.

---

## ⚖️ License

SupraWall Security Scan is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.

© 2026 SupraWall Contributors.
