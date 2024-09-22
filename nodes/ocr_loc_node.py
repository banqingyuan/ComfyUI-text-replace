import torch
import numpy as np
from .api.ocr_loc import web_image_ocr
from .api.rectangle_merge import process_image_with_rectangles
from PIL import Image
from io import BytesIO

def tensor_to_pil(image: torch.Tensor) -> Image.Image:
    """将torch.Tensor转换为PIL Image"""
    if len(image.shape) == 4:
        image = image.squeeze(0)
    return Image.fromarray((image * 255).byte().cpu().numpy().astype(np.uint8))

def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    """将PIL Image转换为torch.Tensor"""
    np_image = np.array(image).astype(np.float32) / 255.0
    return torch.from_numpy(np_image).unsqueeze(0)

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
        # 将torch.Tensor转换为PIL Image
        img_pil = tensor_to_pil(image)

        # 将PIL Image转换为字节流
        buffer = BytesIO()
        img_pil.save(buffer, format="JPEG")
        image_data = buffer.getvalue()

        # 调用OCR API
        ocr_result = web_image_ocr(image_data, access_token)

        if "words_result" not in ocr_result:
            print("OCR识别失败")
            return (image,)

        # 收集所有矩形
        rectangles = [
            [word["location"]["left"], word["location"]["top"], 
             word["location"]["width"], word["location"]["height"]]
            for word in ocr_result["words_result"]
        ]

        # 处理图像
        processed_image = process_image_with_rectangles(np.array(img_pil), rectangles)

        # 将处理后的图像转换回torch.Tensor
        processed_tensor = pil_to_tensor(Image.fromarray(processed_image))

        return (processed_tensor,)
