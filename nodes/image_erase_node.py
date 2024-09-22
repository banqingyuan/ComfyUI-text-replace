import torch
import numpy as np
from PIL import Image
import json
from .api.text_erase import image_inpainting
from .util import *

class ImageEraseNode:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "rectangles": ("STRING", {
                    "multiline": True,
                    "default": "[[0, 0, 100, 100]]"
                }),
                "expand_pixels": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100,
                    "step": 1,
                }),
                "access_token": ("STRING", {
                    "multiline": False,
                    "default": "请输入您的百度AI平台access token"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "erase_image"
    CATEGORY = "Image Processing"

    def erase_image(self, image: torch.Tensor, rectangles: str, expand_pixels: int, access_token: str):
        # 将输入的字符串转换为列表
        rectangles = json.loads(rectangles)

        # 获取图像尺寸
        height, width = image.shape[1:3]

        # 扩展矩形并处理边界情况
        expanded_rectangles = []
        for rect in rectangles:
            left = max(0, rect[0] - expand_pixels)
            top = max(0, rect[1] - expand_pixels)
            right = min(width, rect[0] + rect[2] + expand_pixels)
            bottom = min(height, rect[1] + rect[3] + expand_pixels)
            expanded_rectangles.append({
                'left': left,
                'top': top,
                'width': right - left,
                'height': bottom - top
            })

        # 将torch tensor转换为PIL图像
        img_pil = tensor_to_pil(image)

        # 将PIL图像转换为字节
        img_byte_arr = pil_to_bytes(img_pil)

        # 调用image_inpainting函数进行图像修复
        result = image_inpainting(img_byte_arr, expanded_rectangles, access_token)

        if result:
            # 将base64编码的结果转换回PIL图像
            erased_img = base64_to_pil(result)
            # 将PIL图像转换回torch tensor
            erased_tensor = pil_to_tensor(erased_img)
            return (erased_tensor,)
        else:
            print("图像擦除失败")
            return (image,)
