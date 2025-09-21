from dify_plugin import DifyPluginEnv, Plugin

plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=1800))  # 30分钟超时，支持长时间运行的实时行情接口

if __name__ == "__main__":
    plugin.run()
