from dify_plugin import ToolProvider

class CardCropProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        # 本地图片处理，无需外部凭据。
        pass
