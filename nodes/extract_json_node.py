import json
import re

class ExtractJSONNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_string": ("STRING", {
                    "multiline": True,
                    "default": "Some text {\"key\": \"value\"} more text"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "extract_json"
    CATEGORY = "Utils"

    def extract_json(self, input_string: str):
        # 使用正则表达式提取{}及其中包含的内容
        pattern = r'\{[^{}]*\}'
        match = re.search(pattern, input_string)

        if match:
            try:
                # 尝试解析提取的字符串为JSON
                json_object = json.loads(match.group())
                
                # 如果解析成功,将JSON对象重新序列化为格式化的JSON字符串
                validated_json = json.dumps(json_object, indent=2, ensure_ascii=False)
                return (validated_json,)
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {str(e)}")

        # 如果没有找到有效的JSON或解析失败,返回空字符串
        return ("",)
