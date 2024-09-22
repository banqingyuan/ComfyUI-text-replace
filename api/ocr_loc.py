import requests
import base64
import json

def web_image_ocr(image_data, access_token):
    """
    网络图片文字识别（含位置版）函数
    
    :param image_data: 图片数据（字节串）
    :param access_token: 百度AI平台的access token
    :return: 识别结果的JSON字符串
    """
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/webimage_loc"
    
    # 对图片数据进行base64编码
    img = base64.b64encode(image_data).decode('utf-8')
    
    params = {"image": img}
    request_url = f"{request_url}?access_token={access_token}"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(request_url, data=params, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        if 'error_code' in result:
            print(f"API Error: {result['error_code']} - {result.get('error_msg', 'Unknown error')}")
        return result
    else:
        print(f"HTTP Error: {response.status_code} - {response.text}")
        return {"error": "请求失败", "status_code": response.status_code}

# 测试用例
def test_web_image_ocr():
    # 请替换为您的access token
    access_token = "24.84c27b3250816ff5baf7954667f9c9f0.2592000.1729578720.282335-115653370"
    image_path = "../script/example.jpeg"
    
    # 读取图片数据
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    result = web_image_ocr(image_data, access_token)
    
    print("网络图片文字识别结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 简单的结果验证
    assert "words_result" in result, "返回结果中应包含 'words_result' 字段"
    assert "words_result_num" in result, "返回结果中应包含 'words_result_num' 字段"
    assert isinstance(result["words_result"], list), "'words_result' 应该是一个列表"
    
    print("测试通过！")

if __name__ == "__main__":
    test_web_image_ocr()