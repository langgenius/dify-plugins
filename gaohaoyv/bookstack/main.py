from __future__ import annotations

from dify_plugin import DifyPluginEnv, Plugin


plugin = Plugin(DifyPluginEnv(MAX_REQUEST_TIMEOUT=120))

def main() -> None:
    plugin.run()


if __name__ == "__main__":
    main()
