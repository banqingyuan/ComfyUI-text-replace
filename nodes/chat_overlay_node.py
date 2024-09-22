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
                    font_size, formatted_text = self.calculate_font_size(rect['width'], rect['height'], text, font_name)
                    font = ImageFont.truetype(os.path.join(font_dir, font_name), font_size)

                    # 在矩形内绘制文本
                    self.draw_text_in_rectangle(draw, rect, formatted_text, font, text_color)

        # 将PIL图像转换回torch tensor
        return (pil2tensor(back_image),)

    def calculate_font_size(self, width, height, text, font_name):
        max_font_size = min(width, height) // 2
        font_size = max_font_size
        font_path = os.path.join(font_dir, font_name)
        
        # 创建一个临时的 ImageDraw 对象来测量文本大小
        temp_image = Image.new('RGB', (1, 1))
        draw = ImageDraw.Draw(temp_image)
        
        while font_size > 1:
            font = ImageFont.truetype(font_path, size=font_size)
            lines = []
            current_line = ""
            words = text.split()
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] <= width * 0.9:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            total_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines)
            
            if total_height <= height * 0.88 and len(lines) > 1:
                break
            
            font_size -= 1
        
        return font_size, "\n".join(lines)

    def draw_text_in_rectangle(self, draw, rect, text, font, color):
        x, y = rect['left'], rect['top']
        w, h = rect['width'], rect['height']
        
        lines = text.split('\n')
        total_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines)
        
        current_y = y + (h - total_height) / 2
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            text_x = x + (w - text_width) / 2
            
            draw.text((text_x, current_y), line, font=font, fill=color)
            current_y += text_height