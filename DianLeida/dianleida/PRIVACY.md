# Privacy Policy - DianLeiDa 1688 Sourcing (Dify plugin)

Last updated: 2026-11-16

This plugin is published by DianLeiDa (https://www.dianleida.net). This policy explains what data the plugin processes when it runs inside your Dify workspace.

## What the plugin processes

1. Credential: the DianLeiDa MCP key URL you paste during authorization. It is stored by Dify in the workspace credential store and used as the request endpoint for every tool call.
2. Request parameters: the filters and identifiers you pass to a tool, such as keyword, offer ID, shop URL, image URL or category IDs.
3. Response data: product, shop and ranking data returned by the DianLeiDa service.

## What the plugin does not do

- It does not collect personal data of end users by itself.
- It does not store request or response data on disk, in a database or in logs beyond what Dify already records for a tool call.
- It does not send data to any endpoint other than the MCP endpoint in the key URL you configured.
- It does not include telemetry, analytics or advertising SDKs.

## Third-party service

Tool calls are executed by the DianLeiDa MCP service. Data sent to that service is handled under DianLeiDa's own terms and privacy policy, available at https://www.dianleida.net. If your workspace policy forbids sending sourcing queries to a third-party service, do not install this plugin.

## Data retention and deletion

The plugin itself retains nothing. To remove the credential, delete the plugin authorization in Dify or uninstall the plugin.

## Contact

Questions about this policy, or a request to delete data held by the service: 3373165051@qq.com
Documentation: https://www.dianleida.net/mcp/docs/
