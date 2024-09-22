import torch
from PIL import Image
import numpy as np
import base64
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

def base64_to_pil(base64_str: str) -> Image.Image:
    """将base64编码的图像转换为PIL Image"""
    image_data = base64.b64decode(base64_str)
    return Image.open(BytesIO(image_data))

def pil_to_bytes(image: Image.Image, format: str = 'JPEG') -> bytes:
    """将PIL Image转换为字节串"""
    buffer = BytesIO()
    image.save(buffer, format=format)
    return buffer.getvalue()