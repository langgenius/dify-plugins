# WeChat Sender Plugin

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Version](https://img.shields.io/badge/version-0.0.1-green.svg)

通过调用GeweChat API实现微信消息自动发送的插件工具

## 功能特性

- 通过API实现微信消息自动发送
- 支持自定义接收者微信ID
- 简单易用的配置界面
- 需要配合开源GeweChat项目使用

## 安装要求

1. 自己搭建的GeweChat服务端，确保网络畅通
2. Python 3.12+

## 配置说明

### 必需参数

| 参数名 | 说明 | 示例值 |
|--------|------|--------|
| `server_url` | GeweChat API服务器地址 | `https://gewe_url:2531/v2/api` |
| `token` | API认证令牌 | `0exxxxxxxxxx13` |
| `appid` | 应用标识ID | `wx_xxxxxxxx` |
| `receiver_id` | 接收者微信ID | `wxid_xxxxxxxx` |

### 获取授权

1. 访问[GeweChat开源项目](https://github.com/Devo919/Gewechat)
2. 按照文档部署服务端
3. 通过api接口获取必须参数，[接口文档](https://apifox.com/apidoc/shared/69ba62ca-cb7d-437e-85e4-6f3d3df271b1/api-266307392)
