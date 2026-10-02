# 550W AI去字幕去水印 for Dify (China)

Remove image watermarks, erase subtitles or visual watermarks from uploaded local videos, and resolve platform watermarks from supported video share links. This native Dify tool provider connects to the [550W Open API](https://qzm.550wai.cn/api-keys) and accepts Dify-selected files; it does not require the standalone Skill or its CLI.

Source: https://github.com/sunshinehu/550w-ai-subtitle-remover · Support: support@550wai.com

## Configure

Get your user number and API key from the [China API key management page](https://qzm.550wai.cn/api-keys), then enter both in the Dify tool provider settings. The API key is a secret field.

This independent China provider supports API Key authentication, not OAuth. Its account and purchase links use the China site regardless of the Dify interface language.

## Tools

- **Remove image watermark** accepts a user-selected PNG, JPEG or WebP image (up to 50 MB), uploads it to 550W and returns the task/result. **Check image task** follows a pending image task.
- **Submit local video** accepts a user-selected MP4/MOV video (up to the 550W service's 1 GiB limit). The adapter streams the Dify file URL to a bounded temporary file before forwarding it, rather than loading the video into plugin memory. Dify's own configured upload limit and the plugin host's free temporary disk space may be lower. The plugin uses the returned video metadata and submits a full-frame erasure task; all four user-supplied rectangle coordinates can narrow the area. A stable idempotency key is required.
- **Check credits** reads the shared account balance without creating a task.
- **Remove short-video watermark** takes a public share link copied inside Douyin, Kuaishou, Bilibili, Weibo or another supported app. A successful result costs one credit. Platform coverage depends on the service response.
- **Submit subtitle-removal task** takes a direct MP4/MOV URL and the video's actual width, height, and duration. It submits a billable full-frame task. Use a stable idempotency key for retries; without one, a repeat may create another billable task.
- **Check subtitle task** reads a submitted task's status and result.

Do not feed a social share page to the subtitle-task tool; use a direct video URL for that operation. Dify must provide an absolute HTTP(S) file URL reachable by its plugin runtime (`FILES_URL`/`INTERNAL_FILES_URL` on self-hosted Dify). Test a file larger than 50 MB and monitor temporary-disk use before claiming larger-video support on a particular Dify installation. An upload response or a submitted task is not proof that processing has completed; check the returned status before presenting a result.

See [privacy information](PRIVACY.md) and the [service terms](https://eraser.550wai.com/terms/). Processing costs and limits are described on the API page. Dify workflows should check the returned `code` before using any result URL.

## 国内版使用说明

上传图片去水印及多余文字；上传本地视频去硬字幕或画面水印，默认全屏处理，坐标区域是可选高级参数。视频链接去水印使用从抖音、快手、哔哩哔哩、微博等 App 或平台网站分享操作复制的链接。解析后的视频链接若下载失败或超时，直接提供解析出来的视频链接供用户在浏览器下载，不冒充已经下载完成。

[获取和管理 API Key](https://qzm.550wai.cn/api-keys) · [积分充值](https://qzm.550wai.cn/purchase?tab=speed)
