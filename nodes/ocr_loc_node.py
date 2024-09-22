import torch
import numpy as np
from .api.ocr_loc import web_image_ocr
from .api.rectangle_merge import process_image_with_rectangles
from PIL import Image
from io import BytesIO

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

    def process_image(self, image: torch.Tensor, access_token: str):
        # 确保输入是单张图像
        if len(image.shape) == 4:
            image = image.squeeze(0)

        # 将torch.Tensor转换为PIL Image
        img_pil = Image.fromarray((image * 255).byte().cpu().numpy().astype(np.uint8))

        # 将PIL Image转换为字节流
        buffer = BytesIO()
        img_pil.save(buffer, format="JPEG")
        image_data = buffer.getvalue()

        # 调用OCR API
        ocr_result = web_image_ocr(image_data, access_token)

        if "words_result" not in ocr_result:
            print("OCR识别失败")
            return (image.unsqueeze(0),)
        

        # 收集所有矩形
        rectangles = [
            [word["location"]["left"], word["location"]["top"], 
             word["location"]["width"], word["location"]["height"]]
            for word in ocr_result["words_result"]
        ]

        # 处理图像
        processed_image = process_image_with_rectangles(np.array(img_pil), rectangles)

        # 将处理后的图像转换回torch.Tensor
        processed_tensor = torch.from_numpy(processed_image).float() / 255.0

        # 确保张量的形状正确 (B, H, W, C)
        processed_tensor = processed_tensor.unsqueeze(0)

        return (processed_tensor,)
