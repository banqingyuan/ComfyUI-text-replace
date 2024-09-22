from .nodes.ocr_loc_node import *
from .nodes.image_erase_node import *

NODE_CLASS_MAPPINGS = {
    "OCRLocNode": OCRLocNode,
    "ImageEraseNode": ImageEraseNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OCRLocNode": "OCR Location Node",
    "ImageEraseNode": "Image Erase Node"
}