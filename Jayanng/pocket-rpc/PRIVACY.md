# Privacy Policy for Pocket RPC

Pocket RPC is a read-only Dify tool plugin. It fetches public on-chain data through Pocket Network's free public RPC endpoints.

## What data this plugin handles

When you use a tool, the plugin sends a standard Ethereum JSON-RPC request to a Pocket Network public endpoint for the chain you selected. The request contains only what the tool needs:

- The chain you selected, which picks the endpoint.
- For the Balance tool, the wallet address you entered.
- For the Transaction tool, the transaction hash you entered.

These values are public blockchain data: wallet addresses and transaction hashes are visible to anyone on the public chain.

## What this plugin does not do

- It does not collect, store, or log any personal data.
- It does not ask for or handle API keys, passwords, seed phrases, or private keys. There is nothing to configure, and no account exists.
- It does not sign anything or send any transaction. All three tools are read-only.
- It does not send data to any party other than the Pocket Network public RPC endpoint for the selected chain.
- It does not use cookies, tracking, or analytics.

## Third parties

Requests go to Pocket Network's free public RPC endpoints (for example https://eth.api.pocket.network). Pocket Network's own privacy policy applies to what their endpoints receive. The plugin itself keeps nothing.

## Contact

Questions about this policy: jayanng300@gmail.com. Source: https://github.com/Jayanng/pocket-rpc
