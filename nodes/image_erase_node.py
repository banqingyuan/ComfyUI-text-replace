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
                "access_token": ("STRING", {
                    "multiline": False,
                    "default": "请输入您的百度AI平台access token"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "erase_image"
    CATEGORY = "Image Processing"

    def erase_image(self, image: torch.Tensor, rectangles: str, access_token: str):
        # 将输入的字符串转换为列表
        rectangles = json.loads(rectangles)

        # 将rectangles转换为image_inpainting所需的格式
        formatted_rectangles = [
            {'width': rect[2], 'top': rect[1], 'height': rect[3], 'left': rect[0]}
            for rect in rectangles
        ]

        # 将torch tensor转换为PIL图像
        img_pil = tensor_to_pil(image)

        # 将PIL图像转换为字节
        img_byte_arr = pil_to_bytes(img_pil)

        # 调用image_inpainting函数进行图像修复
        result = image_inpainting(img_byte_arr, formatted_rectangles, access_token)

        if result:
            # 将base64编码的结果转换回PIL图像
            erased_img = base64_to_pil(result)
            # 将PIL图像转换回torch tensor
            erased_tensor = pil_to_tensor(erased_img)
            return (erased_tensor,)
        else:
            print("图像擦除失败")
            return (image,)
