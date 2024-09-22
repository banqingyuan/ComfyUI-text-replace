import torch
from PIL import Image
import numpy as np

def tensor_to_pil(image: torch.Tensor) -> Image.Image:
    """将torch.Tensor转换为PIL Image"""
    if len(image.shape) == 4:
        image = image.squeeze(0)
    return Image.fromarray((image * 255).byte().cpu().numpy().astype(np.uint8))

def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    """将PIL Image转换为torch.Tensor"""
    np_image = np.array(image).astype(np.float32) / 255.0
    return torch.from_numpy(np_image).unsqueeze(0)