# Privacy - Prompt Efficiently for Dify

This plugin connects your Dify workspace to your own Prompt Efficiently account.

## What leaves your Dify workspace

- **Sign-in**: your account email and the 6-digit code you paste are sent to promptefficiently.com to create a session. The session token is stored in Dify's plugin storage, keyed by your email, and reused until it expires.
- **Estimate prompt cost**: only a random request id is sent to promptefficiently.com, to count the estimate against your account's allowance. The prompt text, the estimate inputs and the results never leave your Dify workspace; the estimation maths runs inside this plugin.
- **Prompt Efficiently rewrite**: the prompt text you pass to this tool is sent to promptefficiently.com and processed by its AI provider to produce the rewrite. This happens only when you have turned on the 18+ consent in the plugin settings.
- **Usage and billing status**: your session token is sent to promptefficiently.com to read your plan and remaining free usage.

## What this plugin stores

Only the session token described above, in Dify's plugin storage. No prompts, estimates, rewrites or results are stored by the plugin.

## What this plugin does not do

No analytics, no tracking, no advertising, no sale of data, no third parties other than promptefficiently.com and the AI provider disclosed on Prompt Efficiently's privacy page.

Full policy: https://promptefficiently.com/privacy
Contact: promptefficiently@gmail.com
