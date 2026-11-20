# Odile Direct for Dify

Use Odile Direct tools in Dify to look up a business by phone, send a request, follow a conversation, or place and check a call.

Install the packaged plugin in Dify under **Plugins**, then add Odile Direct tools to an agent or workflow. An HTTPS connection to odilelabs.com is required. Directory lookups need no API key; an optional key from [Developers](https://odilelabs.com/developers) raises the free allowance. Other actions may require a key or credits; see [pricing](https://odilelabs.com/pricing).

Use `find_business_agent` first to get a business ID. Read the returned task status before reporting a message or booking as complete. For `send_to_business`, enter `data` as a JSON object string. For `call_business`, enter optional `questions` as a JSON array string. Supply a new `message_id` for each new request and reuse it on retries. When omitted for `send_to_business`, the plugin derives one from the business, skill, and data; identical inputs will produce the same ID even on a later day.

Source: https://github.com/tolga-boop/dify-plugin-odile
Contact: hello@odilelabs.com (Odile Labs, OdileUSA L.L.C.)
Prices and the free allowance: https://odilelabs.com/pricing · Developer docs: https://odilelabs.com/developers
