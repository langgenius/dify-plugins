# 喵喵阅读前端插件 (Reading Scene)

一个用于Dify平台的插件，提供动态SVG场景渲染和用户交互功能，包含可交互的猫咪元素。

## 功能特点

- 提供多种主题的阅读场景：温馨、户外、奇幻、现代
- 根据阅读内容智能调整场景效果
- 支持多种交互方式：点击、悬停、拖拽
- 提供动画效果增强阅读体验
- **新增**: 可交互的猫咪元素，响应用户滚动和鼠标移动
- **新增**: 支持内嵌JavaScript，实现滚动监听和动态变化

## 安装

1. 在Dify平台中添加此插件
2. 配置插件权限和设置
3. 开始在您的应用中使用

## 使用方法

### 渲染场景

```python
result = plugin.render_scene({
    "content": "这是一段阅读内容，描述了温暖的场景...",
    "theme": "cozy"  # 可选: cozy, outdoor, fantasy, modern
})

# 获取SVG内容
svg_content = result["svg_content"]

# 获取动画数据
animation_data = result["animation_data"]
```

### 处理交互

```python
response = plugin.handle_interaction({
    "interaction_type": "click",  # 可选: click, hover, drag
    "element_id": "text_title",   # 特殊元素: cat, magic_cat, tech_cat
    "position": {"x": 150, "y": 200}
})

# 获取响应动作
action = response["response_action"]

# 获取更新数据
update_data = response["update_data"]
```

## 示例

### 基本场景渲染

```python
# 渲染温馨阅读场景
cozy_scene = plugin.render_scene({
    "content": "小猫在温暖的阳光下打盹，书架上摆满了各种精美的书籍...",
    "theme": "cozy"
})

# 渲染奇幻阅读场景
fantasy_scene = plugin.render_scene({
    "content": "魔法森林中，神秘的光芒照亮了古老的魔法书...",
    "theme": "fantasy"
})
```

### 猫咪交互示例

```python
# 点击猫咪
cat_response = plugin.handle_interaction({
    "interaction_type": "click",
    "element_id": "cat",
    "position": {"x": 180, "y": 400}
})

# 猫咪可能的反应: purr, mew, stretch, blink, tilt_head
reaction = cat_response["update_data"]["reaction"]
```

## SVG交互功能

插件生成的SVG包含内嵌JavaScript，能够实现以下交互效果：

1. **滚动响应**：随着用户阅读进度改变猫咪尾巴形状
2. **鼠标跟踪**：猫咪眼睛会跟随鼠标移动
3. **主题元素动画**：
   - 温馨主题：光线闪烁效果
   - 户外主题：太阳呼吸动画
   - 奇幻主题：星星闪烁和魔法光环旋转
   - 现代主题：进度条动态更新

示例交互脚本：

```javascript
// 滚动监听示例
document.addEventListener('scroll', function() {
    const scrollPercent = window.scrollY / (document.body.scrollHeight - window.innerHeight);
    const tail = document.getElementById("tail");
    
    // 根据滚动位置改变猫咪尾巴形状
    if(scrollPercent > 0.7) {
        tail.setAttribute("d", "M-5,-20 Q-10,-45 -30,-35");
    } else if(scrollPercent > 0.4) {
        tail.setAttribute("d", "M-5,-20 Q-20,-30 -35,-15");
    } else {
        tail.setAttribute("d", "M-5,-20 Q-30,-40 -40,-20");
    }
});
```

## 开发

### 环境设置

1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 运行测试：`pytest`

### 贡献指南

欢迎提交PR和Issues，我们将非常感谢您的贡献！

## 许可证

MIT

## 联系方式

作者：Tully-L
邮箱：2332486893@qq.com 