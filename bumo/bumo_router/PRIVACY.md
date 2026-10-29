# Privacy Policy / 隐私说明

**English**

This plugin sends the prompts, files and parameters of each model call, together with your API key, to Bumo Router (`router.bumo.cc` or `router.bumo.ai`, or the custom base URL you configure), which forwards them to the model vendor you selected. The plugin itself stores nothing: it keeps no logs, no conversation content and no copy of your key. To tell which site your key belongs to, it sends one request with a placeholder model name when you save the key; this request is not billed.

Requests carry the headers `X-Title: Dify` and `HTTP-Referer: https://dify.ai/` so that your Bumo Router usage page can show which calls came from Dify. Bumo Router processes data under its own privacy policy, available on its website.

**中文**

本插件把每次模型调用的提示词、文件和参数连同你的 API Key 发送到不墨 Router（`router.bumo.cc` / `router.bumo.ai`，或你配置的自定义地址），再由不墨 Router 转发给你选择的模型厂商。插件本身不存储任何数据：不记日志、不保存对话内容、不保存 Key。保存 Key 时，插件会用一个占位模型名发一次请求来识别 Key 属于哪个站点，该请求不计费。

请求带有 `X-Title: Dify` 和 `HTTP-Referer: https://dify.ai/` 两个请求头，用于在不墨 Router 的用量页区分来自 Dify 的调用。不墨 Router 按其官网公布的隐私政策处理数据。
