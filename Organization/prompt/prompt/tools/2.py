

data={
  "json_string": [
    {
      "assistant_value": "答案是demo",
      "system_value": "你是一个专业的翻译官，使用金庸《倚天屠龙记》里九阳真经的口诀进行翻译以下内容，从{source_language}翻译到{target_language}",
      "text_value": 66,
      "user_value": "待翻译内容: {text}"
    }
  ]
}


def main(data: dict) -> dict:
    try:
        assistant_value = data['json'][0]['assistant_value']
        system_value = data['json'][0]['system_value']
        text_value = data['json'][0]['text_value']
        user_value = data['json'][0]['user_value']
        print(assistant_value)
        return {
            'assistant_value': assistant_value,
            'system_value': system_value,
            'text_value': text_value,
            'user_value': user_value
        }

    except (KeyError, IndexError, TypeError) as e:
        return {'result': None}



main(data)