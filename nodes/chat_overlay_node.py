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
        font_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "fonts")
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
                    font_size = self.calculate_font_size(rect['width'], rect['height'], text, font_name)
                    font = ImageFont.truetype(os.path.join(font_dir, font_name), font_size)

                    # 在矩形内绘制文本
                    self.draw_text_in_rectangle(draw, rect, text, font, text_color)

        # 将PIL图像转换回torch tensor
        return (pil2tensor(back_image),)

    def calculate_font_size(self, width, height, text, font_name):
        max_font_size = min(width, height) // 2
        font_size = max_font_size
        font_path = os.path.join(font_dir, font_name)
        
        # 创建一个临时的 ImageDraw 对象来测量文本大小
        temp_image = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(temp_image)
        
        text_lines = text.split('\n')[:2]  # 只考虑前两行
        
        if len(text_lines) == 2:
            font_size = min(height // 2, max_font_size)
        
        while font_size > 1:
            font = ImageFont.truetype(font_path, size=font_size)
            max_text_width = max(draw.textbbox((0, 0), line, font=font)[2] for line in text_lines)
            text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in text_lines)
            
            if max_text_width <= width * 0.9 and text_height <= height * 0.88:
                break
            
            font_size -= 1
        
        return font_size

    def draw_text_in_rectangle(self, draw, rect, text, font, color):
        x, y = rect['left'], rect['top']
        w, h = rect['width'], rect['height']
        
        # 获取文本大小
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # 计算文本位置（居中）
        text_x = x + (w - text_width) / 2
        text_y = y + (h - text_height) / 2
        
        # 绘制文本
        draw.text((text_x, text_y), text, font=font, fill=color)