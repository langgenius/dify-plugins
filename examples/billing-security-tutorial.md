# 🛡️🧱 Multi-Agent Billing Security with SupraWall

This example demonstrates how to secure a **LangGraph** multi-agent workflow using the **SupraWall** security layer. 

### 🏁 THE SCENARIO: The "AI Billing Desk" 🏁
In a production multi-agent system, a single prompt can trigger a cascade of actions. If an agent is compromised or follows a hallucinated path, it could trigger un-authorized refunds or delete sensitive ops logs.

This workflow isolates three distinct roles:
1.  **Support Node**: General inquiries (Low risk).
2.  **Refund Node**: Financial transactions (High risk—requires $50 limits).
3.  **Ops Node**: System deletions (Critical risk—requires Human-in-the-Loop).

### 🛡️ THE SUPRAWALL LAYER
SupraWall enforces these policies at the **Callback level**. Instead of writing complex `if/else` logic inside your agents, you define a **Deterministic Wall** that blocks non-compliant network calls and tool executions before they reach your backend.

```python
from langgraph.graph import StateGraph, END
from suprawall import SupraWallCallbackHandler

# Enforce a $50 refund limit gate
suprawall_refund_policy = {
    "agent_id": "billing-refund-agent",
    "policies": [
        {
            "tool": "process_refund",
            "constraints": {"max_amount": 50}
        }
    ]
}

# The SupraWall Callback enforces this transparently
handler = SupraWallCallbackHandler(api_key="YOUR_SUPRAWALL_AUTH")
```

### 🧱 WHY THIS MATTERS
By moving security from the **Agent Code** to the **Gateway**, you achieve:
- **Blast Radius Containment**: A support agent cannot technically trigger a refund tool.
- **Forensic Audit Logs**: Every blocked action is logged at the network layer, not just in stdout.
- **HITL Enforcement**: High-risk deletions in the `Ops` node are stalled for human approval via the SupraWall Dashboard.

---
**Check out the full implementation in the [SupraWall Documentation](https://supra-wall.com/docs/examples/billing-workflow).**
