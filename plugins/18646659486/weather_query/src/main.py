import requests


def get_weather(city: str):
    """
    根据城市名称获取当前天气信息。
    这个函数会被 Dify 作为插件工具调用。
    """
    # 这里用 wttr.in 这个免费天气接口，直接用城市名查询
    url = f"https://wttr.in/{city}?format=j1"

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # 取当前天气
        current = data["current_condition"][0]

        result = {
            "city": city,
            "temperature_c": current.get("temp_C"),
            "humidity": current.get("humidity"),
            "weather": current.get("weatherDesc", [{}])[0].get("value"),
            "feels_like_c": current.get("FeelsLikeC"),
            "wind_speed_kmph": current.get("windspeedKmph")
        }

        return result
    except Exception as e:
        # 出错时返回 error 字段，避免插件直接崩
        return {
            "error": f"天气查询失败: {e}"
        }
