from dify_plugin import Plugin
from dify_plugin.config.config import DifyPluginEnv

# 从 .env 文件自动加载配置
config = DifyPluginEnv()
plugin = Plugin(config)

if __name__ == "__main__":
    plugin.run()
