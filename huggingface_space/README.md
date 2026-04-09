---
title: 🧱 SupraWall Security Gateway for Agents
emoji: 🛡️
colorFrom: blue
colorTo: blue
sdk: gradio
sdk_version: 4.25.0
app_file: app.py
pinned: false
license: apache-2.0
short_description: Zero-Trust firewall for smolagents.
python_version: 3.12
tags:
  - agents
  - security
  - smolagents
  - firewall
  - zero-trust
---

# 🧱 SupraWall: The Security Layer for AI Agents

Welcome to the **SupraWall x smolagents** demo! 

## 🛡️ What is SupraWall?

SupraWall is the first **Zero-Trust Semantic Firewall** designed specifically for AI agents and agentic workflows. As agents become more autonomous, the risk of "jailbreaking" and unauthorized tool execution increases. SupraWall sits between your agent and its tools, enforcing policies in real-time based on the *intent* and *impact* of the action.

## 🚀 Key Features

*   **Native smolagents Integration**: Protect any agentic tool with a single line of code.
*   **Layer 2 Semantic Firewall**: Go beyond regular expressions. Our engine understands if an agent is trying to do something malicious, even if it's cleverly phrased.
*   **Zero-Trust Architecture**: No tool is trusted by default. Every call is validated by an out-of-band policy engine.
*   **Human-in-the-Loop**: Pause sensitive actions (like sending an email or deleting a file) for human approval without breaking the agent loop.
*   **Audit Logging**: Every tool call, attempt, and block is logged for enterprise compliance (SOC2/GDPR/EU AI Act).

## 🛠️ Quick Start (smolagents)

```python
from smolagents import CodeAgent, HfModel
from suprawall import wrap_smolagents, SupraWallOptions

# 1. Initialize your model and agent
model = HfModel()
agent = CodeAgent(tools=[my_file_tool, my_web_tool], model=model)

# 2. Add SupraWall protection
agent = wrap_smolagents(agent, SupraWallOptions(
    api_key="your_api_key_here"
))

# 3. Rest easy knowing your agent is secured
agent.run("Let me delete all user files.") # Blocked! 🧱
```

## 🌐 Community & Open Source

SupraWall is built by security engineers for the AI community. 

*   **Website**: [https://www.supra-wall.com](https://www.supra-wall.com)
*   **Docs**: [https://docs.supra-wall.com](https://docs.supra-wall.com)
*   **GitHub**: [SupraWall-Private](https://github.com/wiserautomation/Supra-Wall-Private) (v1.0.0 Stable)

### 🚨 Stay Secure, Build Faster.
Add SupraWall to your agent today and prevent the next "Prompt Injection" headline.
