## metastudio_dify_app

**Author:** zxi2002<zix2002@gmail.com>
**Version:** 0.0.1
**Type:** extension

### 描述

提供将 Dify App 适配华为 MetaStudio 第三方 LLM 接口的扩展插件

### 安装插件

1. Install the extension

- 选择 `本地插件` 安装

2. 配置插件

- 点击插件，点击 `+` 新增`API 端点`
- 填写`端点名称`， 例如 /meta-studio/chat
- 填写`BASE URL`, `dify` 对外的访问地址，例如 http://localhost:1438, https://dify.yourdomain.com
- 填写`API Key`, 例如 `sk-xxxxxx`
- 选择 `App` 和 `记忆模式`
- 点击 `保存`

如果显示`服务正常`，则配置成功

3. 使用插件

复制对外的 url, 例如 `http://localhost:1438/e/1m4lpn4s7i3tb523/metastudio_dify_app/chat`,
其中 `1m4lpn4s7i3tb523` 对应 `MetaStudio` 的 `App ID`

在 `MetaStudio` 的 `互动数字人` 页面，需要配置的3个参数分别为

- `APPID`: `1m4lpn4s7i3tb523`
- `APPKey`: `sk-xxxxxx`
- `第三方语言模型地址`: `http://localhost:1438/e/1m4lpn4s7i3tb523/metastudio_dify_app/chat`

### 开发

1. 初始化开发工具

如果开发别的插件，请参考[初始化开发工具](https://docs.dify.ai/zh-hans/plugins/quick-start/develop-plugins/initialize-development-tools)

2. 下载代码

```bash
git clone https://codeup.aliyun.com/6551e78531f0722ce703195e/nebula-ai/metastudio-dify-app.git
```

3. 安装依赖

```bash
cd metastudio-dify-app
pip install -r requirements.txt
```

4. 配置
   在根目录下创建 `.env` 文件, 添加一下内容, 其中 `REMOTE_INSTALL_KEY` 从 `dify` 的插件页面获取

```env
INSTALL_METHOD=remote
REMOTE_INSTALL_HOST=remote
REMOTE_INSTALL_PORT=5003
REMOTE_INSTALL_KEY=****-****-****-****-****
```

5. 运行

```bash
python -m main
```

如果不报错，刷新 `dify` 的插件页面，即可看到插件

6. 发布和打包

打包命令

```bash
# 将 ./metastudio-dify-app 为插件项目的实际路径
dify plugin package ./metastudio-dify-app
```

### 注意

1. 如果要本地安装插件，请修改 `/docker/.env` 文件, 将 `FORCE_VERIFYING_SIGNATURE` 设置为 `false`

```env
FORCE_VERIFYING_SIGNATURE=false
```

然后重启 `dify` 容器, 刷新页面后，再重新安装插件

```bash
docker compose down
docker compose up -d
```

2. 如果你的扩展的 APP 是 `Agent 模式`，则只能使用 `stream` 模式
请在 `MetaStudio` 的 `互动数字人` 配置页面，将 `流式响应` 打开


