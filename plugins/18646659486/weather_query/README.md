# weather_query 天气查询插件

一个简单的 Python 插件，可通过城市名称实时查询天气信息，适用于 Dify 等插件平台。

## 功能简介
- 输入城市名，获取当前温度、湿度、天气描述、体感温度、风速等信息
- 使用 wttr.in 免费天气 API
- 错误处理友好，接口稳定

## 文件结构
```
weather_plugin/
  main.py            # 插件主逻辑，定义 get_weather 工具
  manifest.json      # 插件元数据与工具描述
  requirements.txt   # 依赖列表（requests）
```

## 快速开始
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 直接调用 `get_weather` 函数，或在 Dify/插件平台注册使用。

   示例：
   ```python
   from main import get_weather
   print(get_weather("北京"))
   ```

3. 也可通过 manifest.json 作为插件工具集成到 Dify 等平台。

## API 说明
- 工具名：`get_weather`
- 参数：
  - `city` (str)：城市名称（如“北京”、“上海”）
- 返回：
  - 查询成功：字典，包含温度、湿度、天气描述等
  - 查询失败：字典，包含 `error` 字段

## 示例返回
```
{
  "city": "北京",
  "temperature_c": "2",
  "humidity": "60",
  "weather": "Clear",
  "feels_like_c": "0",
  "wind_speed_kmph": "10"
}
```

## 依赖
- requests

## 作者
编程小萌新

---
如有建议欢迎 issue 或 PR！