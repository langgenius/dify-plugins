import logging
from dify_plugin import Plugin, DifyPluginEnv

# 设置日志级别为debug
logging.basicConfig(level=logging.DEBUG)

# Now supporting both SSE and streamable_http transports for MCP communication.
# To use streamable_http, pass transport="streamable_http" when using McpClientsUtil functions
plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))

if __name__ == '__main__':
    plugin.run()
