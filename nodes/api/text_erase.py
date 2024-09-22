import requests
import base64
import json

def image_inpainting(image_data, rectangle: list, access_token: str):
    """
    调用百度智能云图像修复接口
    
    :param image_data: 图片数据（字节串）
    :param rectangle: 要修复的矩形区域，格式为 [{'width': int, 'top': int, 'height': int, 'left': int}]
    :param access_token: 百度智能云API的access token
    :return: 修复后的图片的base64编码
    """
    url = "https://aip.baidubce.com/rest/2.0/image-process/v1/inpainting"
    
    # 对图片数据进行base64编码
    image = base64.b64encode(image_data).decode('utf-8')
    
    # 构造请求参数
    params = {
        "rectangle": rectangle,
        "image": image
    }
    
    # 构造请求头
    headers = {
        'Content-Type': 'application/json'
    }
    
    # 发送POST请求
    response = requests.post(f"{url}?access_token={access_token}", 
                             headers=headers, 
                             data=json.dumps(params))
    
    # 解析响应
    if response.status_code == 200:
        result = response.json()
        if 'image' in result:
            return result['image']
        else:
            print(f"Error: {result.get('error_msg', 'Unknown error')}")
            return None
    else:
        print(f"HTTP Error: {response.status_code}")
        return None

# 使用示例
if __name__ == "__main__":
    # 读取图片数据
    with open("../script/example.jpeg", "rb") as f:
        image_data = f.read()
    
    rectangle = [{'width': 92, 'top': 95, 'height': 36, 'left': 543}]
    access_token = "24.84c27b3250816ff5baf7954667f9c9f0.2592000.1729578720.282335-115653370"
    
    result = image_inpainting(image_data, rectangle, access_token)
    if result:
        # 将修复后的图片保存到文件
        with open("inpainted_image.jpg", "wb") as f:
            f.write(base64.b64decode(result))
        print("修复后的图片已保存为 inpainted_image.jpg")
    else:
        print("图像修复失败")