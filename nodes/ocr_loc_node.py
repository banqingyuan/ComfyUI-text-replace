import torch
import cv2
import numpy as np
from .api.ocr_loc import web_image_ocr
from .api.rectangle_merge import merge_rectangles, process_image_with_rectangles
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

    def process_image(self, image, access_token):
        # 将torch.tensor转换为numpy数组，然后转为PIL Image
        i = 255. * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8).squeeze())

        # 将PIL Image转换为字节流
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        image_data = buffer.getvalue()

        # 调用OCR API
        ocr_result = web_image_ocr(image_data, access_token)

        if "words_result" not in ocr_result:
            print("OCR识别失败")
            return (image,)

        # 收集所有矩形
        rectangles = []
        for word in ocr_result["words_result"]:
            loc = word["location"]
            rectangles.append([
                loc['left'],
                loc['top'],
                loc['width'],
                loc['height']
            ])

        # 将PIL Image转换为numpy数组
        image_np = np.array(img)

        # 处理图像
        processed_image = process_image_with_rectangles(image_np, rectangles)

        # 确保处理后的图像是3通道的
        if len(processed_image.shape) == 2:
            processed_image = np.stack([processed_image] * 3, axis=-1)

        # 将处理后的图像转换回torch.tensor
        processed_tensor = torch.from_numpy(processed_image).float() / 255.0
        processed_tensor = processed_tensor.permute(2, 0, 1).unsqueeze(0)

        # 确保张量的形状是 (1, 3, H, W)
        if processed_tensor.shape[1] != 3:
            processed_tensor = processed_tensor.repeat(1, 3, 1, 1)

        return (processed_tensor,)
