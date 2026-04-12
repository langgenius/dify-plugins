# langchain-suprawall

This is the official [SupraWall](https://supra-wall.com) plugin for LangChain and LangGraph in Python.

It provides a specialized `BaseCallbackHandler` that intercepts tool executions and asks the SupraWall gateway for permission based on the current agent's identity, enforcing centralized, role-based network security even if the LLM is compromised via prompt injection.

## Installation

```bash
pip install langchain-suprawall
```

## Quick Start

```python
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_suprawall import SupraWallCallbackHandler

# 1. Initialize the callback handler with your agent's identity
sw_callback = SupraWallCallbackHandler(
    api_key=os.environ.get("SUPRAWALL_API_KEY"),
    agent_id="support-agent"
)

# 2. Attach it to your agent or graph invocation
model = ChatOpenAI(model="gpt-4-turbo-preview")
model.invoke(
    [HumanMessage(content="Hello!")],
    config={"callbacks": [sw_callback]}
)
```

## Official Examples

To see how to build a production-grade multi-agent system using LangGraph and SupraWall, please see our official example in the LangGraph repository:

* [Multi-Agent Billing Desk with SupraWall Security](https://github.com/langchain-ai/langgraph/tree/main/examples/suprawall-billing-desk)
