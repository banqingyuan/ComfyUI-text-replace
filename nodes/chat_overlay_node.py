import numpy as np
import torch
import os
import platform
import json
from PIL import Image, ImageDraw, ImageFont
from .config import color_mapping, COLORS
from .util import *

ALIGN_OPTIONS = ["center", "top", "bottom"]
ROTATE_OPTIONS = ["text center", "image center"]
JUSTIFY_OPTIONS = ["center", "left", "right"]
PERSPECTIVE_OPTIONS = ["top", "bottom", "left", "right"]

class OverlayText:

    @classmethod
    def INPUT_TYPES(s):
        font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "fonts")
        file_list = [f for f in os.listdir(font_dir) if os.path.isfile(os.path.join(font_dir, f)) and f.lower().endswith(".ttf")]

        return {"required": {
                "image": ("IMAGE",),
                "rectangles": ("STRING", {"multiline": True, "default": "[{\"id\": 1, \"left\": 0, \"top\": 0, \"width\": 100, \"height\": 100}]"}),
                "texts": ("STRING", {"multiline": True, "default": "{\"1\": \"Sample Text\"}"}),
                "font_name": (file_list,),
                "font_color": (COLORS,),
                "font_color_hex": ("STRING", {"multiline": False, "default": "#000000"}),
                }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "overlay_text"
    CATEGORY = "Image Processing"

    def overlay_text(self, image, rectangles, texts, font_name, font_color, font_color_hex='#000000'):
        # 解析输入的JSON字符串
        rectangles = json.loads(rectangles)
        texts = json.loads(texts)

        # 获取RGB值
        text_color = get_color_values(font_color, font_color_hex, color_mapping)

        # 转换tensor图像
        image_3d = image[0, :, :, :]
        back_image = tensor2pil(image_3d)

        # 创建一个绘图对象
        draw = ImageDraw.Draw(back_image)

        for rect in rectangles:
            rect_id = str(rect['id'])
            if rect_id in texts and texts[rect_id]:
                text = texts[rect_id].strip()
                if text:  # 添加对空字符串的跳过逻辑
                    # 计算适合矩形的字体大小
                    font_size = self.calculate_font_size(rect['width'], rect['height'], text)
                    font = ImageFont.truetype(os.path.join(font_dir, font_name), font_size)

                    # 在矩形内绘制文本
                    self.draw_text_in_rectangle(draw, rect, text, font, text_color)

        # 将PIL图像转换回torch tensor
        return (pil2tensor(back_image),)

    def calculate_font_size(self, width, height, text):
        # 这里可以实现更复杂的字体大小计算逻辑
        return min(width // len(text), height) // 2

    def draw_text_in_rectangle(self, draw, rect, text, font, color):
        x, y = rect['left'], rect['top']
        w, h = rect['width'], rect['height']
        
        # 获取文本大小
        text_width, text_height = draw.textsize(text, font=font)
        
        # 计算文本位置（居中）
        text_x = x + (w - text_width) / 2
        text_y = y + (h - text_height) / 2
        
        # 绘制文本
        draw.text((text_x, text_y), text, font=font, fill=color)