<div align="center">

# 🛡️ ProofCore Notary Plugin for Dify

**Zero-Auth Cryptographic Notarization & Evidence Layer on the TON Blockchain.**

[![ProofCore Protocol](https://img.shields.io/badge/ProofCore-Protocol-00d2ff)](https://proofcore.org)
[![TON Blockchain](https://img.shields.io/badge/Blockchain-TON-0098EA?logo=ton&logoColor=white)](https://ton.org)

</div>

This is the official **Dify Plugin** for the ProofCore Protocol. It allows your autonomous Dify workflows and AI agents to cryptographically seal their generated reports, audits, and agreements on the TON Blockchain to prove provenance and prevent tampering.

## 🚀 How to Install in Dify

1. Open your Dify Dashboard.
2. Navigate to **Plugins** in the top navigation bar.
3. Click on **Install from GitHub**.
4. Paste the URL of this repository:
   ```text
   https://github.com/ProofCore-Protocol/dify-proofcore-plugin
   ```
5. Click **Install**. The `ProofCore Notary` tool will now be available in your workspace!

## 🛠 How to Use in Workflows

1. In Dify Studio, open your Agent or Workflow.
2. Add a new **Tool** node and select **ProofCore Notary -> Seal Content**.
3. Pass the generated text (e.g., an audit report) to the `content` input.
4. The tool will automatically hash the content, queue it for Merkle Tree batching on the TON Blockchain, and return a verifiable citation badge.
5. *Crucial:* Instruct your LLM to append the returned citation string to its final output to the user.

## 🔍 Verification

The tool returns a citation link (e.g., `https://proofcore.org/app/<UUID>`). Anyone can click this link to independently verify the cryptographic hash, Merkle path, and TON transaction block.

> *"Don't trust ProofCore. Verify the proof yourself."*
