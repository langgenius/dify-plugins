from dify_plugin import Plugin, DifyPluginEnv
import logging

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))

# 配置全局日志系统
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 输出到控制台
    ]
)

# 设置特定模块的日志级别
# 将Dify插件系统内部的日志级别设置为WARNING，这样只会显示警告和错误，不会显示INFO
logging.getLogger('dify_plugin').setLevel(logging.WARNING)
# 如果只想屏蔽特定模块，可以更精确地设置
logging.getLogger('dify_plugin.core.server.tcp.request_reader').setLevel(logging.WARNING)

if __name__ == '__main__':
    plugin.run()
