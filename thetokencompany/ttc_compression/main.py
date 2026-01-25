from dify_plugin import Plugin
from dify_plugin.config.config import DifyPluginEnv

config = DifyPluginEnv()
plugin = Plugin(config)

if __name__ == "__main__":
    plugin.run()
