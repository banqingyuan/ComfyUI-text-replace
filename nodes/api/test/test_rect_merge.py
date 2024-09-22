import cv2
import json
import numpy as np
import os
from api.rectangle_merge import process_image_with_rectangles

def test_rectangle_merge():
    # 加载JSON数据
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, 'coordinates.json')
    with open(json_path, 'r') as f:
        data = json.load(f)

    # 加载图片
    image_path = os.path.join(current_dir, 'example2.jpeg')
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"无法读取图像文件: {image_path}")

    # 收集所有矩形
    rectangles = []
    for word in data['words_result']:
        loc = word['location']
        rectangles.append([loc['left'], loc['top'], loc['width'], loc['height']])

    # 处理图像
    processed_image = process_image_with_rectangles(image, rectangles)

    # 保存结果图片
    output_path = os.path.join(current_dir, 'output_image_numbered.jpg')
    cv2.imwrite(output_path, processed_image)

    print(f"处理完成，结果已保存为 '{output_path}'")

    # 简单的结果验证
    assert os.path.exists(output_path), "输出文件应该存在"
    assert cv2.imread(output_path) is not None, "应该能够读取输出的图像文件"

    print("测试通过！")

if __name__ == "__main__":
    test_rectangle_merge()
