#!/bin/bash

# 腾讯云联网搜索API插件构建脚本

echo "🚀 开始构建腾讯云联网搜索API插件..."

# 检查dify是否安装
if ! command -v dify &> /dev/null; then
    echo "❌ dify 未安装，请使用 brew install dify 安装"
    exit 1
fi

# 清理缓存文件
echo "🧹 清理缓存文件..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# 验证插件结构
echo "✅ 验证插件结构..."
if dify plugin validate .; then
    echo "✅ 插件结构验证通过"
else
    echo "❌ 插件结构验证失败"
    exit 1
fi

# 打包插件
echo "📦 打包插件..."
cd ..
if dify plugin package tencent_cloud_search_plugin; then
    echo "✅ 插件打包成功"
    echo "📁 生成的包文件："
    ls -la *.difypkg 2>/dev/null || echo "未找到.difypkg文件"
    # 将包文件移动到插件目录
    mv *.difypkg tencent_cloud_search_plugin/ 2>/dev/null || true
    cd tencent_cloud_search_plugin
    ls -la *.difypkg 2>/dev/null || echo "未找到.difypkg文件"
else
    echo "❌ 插件打包失败"
    cd tencent_cloud_search_plugin
    exit 1
fi

echo "🎉 构建完成！"
echo ""
echo "📋 下一步操作："
echo "1. 将生成的 .difypkg 文件上传到Dify"
echo "2. 配置腾讯云API密钥"
echo "3. 开始使用搜索功能"
echo ""
echo "📖 详细安装说明请参考 INSTALL.md"