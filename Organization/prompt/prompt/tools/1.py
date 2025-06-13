import json

# 假设data_str是Dify节点输出的JSON字符串
data_str ='''
{
  "text": "",
  "files": [],
  "data": [
    {
      "assistant_value": "答案是demo",
      "system_value": "你是一个专业的翻译官，使用金庸《倚天屠龙记》里九阳真经的口诀进行翻译以下内容，从{source_language}翻译到{target_language}",
      "text_value": null,
      "user_value": "待翻译内容: {text}"
    }
  ]'''



def main(data: dict) -> dict:
    try:
        assistant_value = data["data"][0]["assistant_value"]
        system_value = data["data"][0]["system_value"]
        text_value = data["data"][0]["text_value"]
        user_value = data["data"][0]["user_value"]
        print(assistant_value)
        print(system_value)
        print(text_value)
        print(user_value)

        return {
            'assistant_value': assistant_value,
            'system_value': system_value,
            'text_value': text_value,
            'user_value': user_value
        }
    except (KeyError, IndexError, TypeError) as e:
        return {'result': f'Error extracting values: {e}'}
