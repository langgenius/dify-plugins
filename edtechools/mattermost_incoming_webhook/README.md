**Author:** Jiahua Cui  
**Version:** 0.0.1  
**Type:** tool  

### Overview

> Mattermost is an open-core, self-hosted collaboration platform that provides persistent chat and ChatOps, workflow and toolchain automation, integrated voice, screen, file, and content sharing, as well as AI-enhanced information synthesis. The platform is designed to be fully extensible, supporting a rich ecosystem of third-party applications and integrations. Mattermost can be easily enhanced and customized through open APIs, developer frameworks, open-source customization, and community-driven enhancements.

This tool utilizes the incoming Webhook feature in Mattermost integrations (allowing external integrations to send messages) to send messages to the corresponding channel.

### Configuration
1. In Mattermost, go to Product menu > Integrations > Incoming Webhook.
> If you don’t have the Integrations option, incoming webhooks may not be enabled on your Mattermost server or may be disabled for non-admins. They can be enabled by a System Admin from System Console > Integrations > Integration Management. Once incoming webhooks are enabled, continue with the steps below.
2. Select Add Incoming Webhook and add a name and description for the webhook. The description can be up to 500 characters.
3. Select the channel to receive webhook payloads, then select Add to create the webhook.
> You will end up with a webhook endpoint that looks like so:
https://your-mattermost-server.com/hooks/xxx-generatedkey-xxx<hr />
Treat this endpoint as a secret. Anyone who has it will be able to post messages to your Mattermost instance.

### Configuring the Mattermost Tool
1. Install the Mattermost tool from the marketplace.  

2. Add the Mattermost node to your workflow.  

3. Paste Incoming Webhook.