from .nodes.ocr_loc_node import *
from .nodes.image_erase_node import *
from .nodes.chat_overlay_node import *
from .nodes.extract_json_node import *

NODE_CLASS_MAPPINGS = {
    "OCRLocNode": OCRLocNode,
    "ImageEraseNode": ImageEraseNode,
    "ChatOverlayNode": OverlayText,
    "ExtractJsonNode": ExtractJSONNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OCRLocNode": "OCR Location Node",
    "ImageEraseNode": "Image Erase Node",
    "ChatOverlayNode": "Chat Overlay Node",
    "ExtractJsonNode": "Extract JSON Node",
}