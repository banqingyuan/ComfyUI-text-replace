import torch
import cv2
import numpy as np
from .api.ocr_loc import web_image_ocr
from .api.rectangle_merge import merge_rectangles, process_image_with_rectangles

class OCRLocNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "access_token": ("STRING", {
                    "multiline": False,
                    "default": "请输入您的百度AI平台access token"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process_image"
    CATEGORY = "Image Processing"

    def process_image(self, image, access_token):
        # 将torch.tensor转换为numpy数组
        image_np = (image.squeeze().permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
        
        # 检查图像尺寸并在必要时调整大小
        max_dimension = 65000
        height, width = image_np.shape[:2]
        scale = 1.0
        if height > max_dimension or width > max_dimension:
            scale = max_dimension / max(height, width)
            new_height = int(height * scale)
            new_width = int(width * scale)
            image_np = cv2.resize(image_np, (new_width, new_height), interpolation=cv2.INTER_AREA)
            print(f"Image resized from {height}x{width} to {new_height}x{new_width}")
        
        # 将图像编码为JPEG格式
        _, img_encoded = cv2.imencode('.jpg', image_np)
        image_data = img_encoded.tobytes()

        # 调用OCR API
        ocr_result = web_image_ocr(image_data, access_token)

        if "words_result" not in ocr_result:
            print("OCR识别失败")
            return (image,)

        # 收集所有矩形，并根据缩放比例调整坐标
        rectangles = []
        for word in ocr_result["words_result"]:
            loc = word["location"]
            rectangles.append([
                int(loc['left'] / scale),
                int(loc['top'] / scale),
                int(loc['width'] / scale),
                int(loc['height'] / scale)
            ])

        # 处理图像
        processed_image = process_image_with_rectangles(image_np, rectangles)

        # 将处理后的图像转换回torch.tensor
        processed_tensor = torch.from_numpy(processed_image).float() / 255.0
        processed_tensor = processed_tensor.permute(2, 0, 1).unsqueeze(0)

        return (processed_tensor,)
