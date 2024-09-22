import base64
import os
from ocr_loc import web_image_ocr
from text_erase import image_inpainting

def expand_rectangle(rect, expand_by, image_width, image_height):
    """
    扩大矩形区域，同时确保不超出图片边界
    """
    return {
        "left": max(0, rect["left"] - expand_by),
        "top": max(0, rect["top"] - expand_by),
        "width": min(image_width - rect["left"], rect["width"] + 2 * expand_by),
        "height": min(image_height - rect["top"], rect["height"] + 2 * expand_by)
    }

def erase_text_from_image(image_path, access_token):
    """
    识别图片中的文字位置并抹除所有文字
    
    :param image_path: 图片路径
    :param access_token: 百度AI平台的access token
    :return: 抹除文字后的图片的base64编码
    """
    # 读取图片数据
    with open(image_path, "rb") as f:
        image_data = f.read()
    
    # 步骤1: 识别文字位置
    ocr_result = web_image_ocr(image_data, access_token)
    
    if "words_result" not in ocr_result:
        print("OCR识别失败")
        return None
    
    # 获取图片尺寸（假设OCR结果中包含图片尺寸信息，如果没有，需要另外获取）
    image_width = ocr_result.get("width", 10000)  # 使用一个大数作为默认值
    image_height = ocr_result.get("height", 10000)
    
    # 步骤2: 准备要抹除的矩形区域，并扩大20像素
    rectangles = []
    for word in ocr_result["words_result"]:
        location = word["location"]
        expanded_rect = expand_rectangle(location, 10, image_width, image_height)
        rectangles.append(expanded_rect)
    
    # 步骤3: 调用图像修复接口抹除文字
    result = image_inpainting(image_data, rectangles, access_token)
    
    return result

if __name__ == "__main__":
    access_token = "24.84c27b3250816ff5baf7954667f9c9f0.2592000.1729578720.282335-115653370"
    abs_path = os.path.abspath(__file__)
    image_path = os.path.join(os.path.dirname(abs_path), "../script/example.jpeg")
    
    result = erase_text_from_image(image_path, access_token)
    
    if result:
        # 将抹除文字后的图片保存到文件
        with open("text_erased_image.jpg", "wb") as f:
            f.write(base64.b64decode(result))
        print("抹除文字后的图片已保存为 text_erased_image.jpg")
    else:
        print("文字抹除失败")