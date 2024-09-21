import cv2
import json
import numpy as np

def should_merge(rect1, rect2, vertical_threshold=5, overlap_threshold=0.5):
    # 检查垂直距离
    vertical_close = abs(rect1[1] + rect1[3] - rect2[1]) <= vertical_threshold or \
                     abs(rect2[1] + rect2[3] - rect1[1]) <= vertical_threshold
    
    # 检查水平重叠
    overlap = min(rect1[0] + rect1[2], rect2[0] + rect2[2]) - max(rect1[0], rect2[0])
    total_width = max(rect1[0] + rect1[2], rect2[0] + rect2[2]) - min(rect1[0], rect2[0])
    overlap_ratio = overlap / min(rect1[2], rect2[2])
    
    return vertical_close and overlap_ratio >= overlap_threshold

def merge_rectangles(rectangles, vertical_threshold=10, overlap_threshold=0.5):
    merged = []
    while rectangles:
        current = rectangles.pop(0)
        merged.append(current)
        i = 0
        while i < len(rectangles):
            if should_merge(current, rectangles[i], vertical_threshold, overlap_threshold):
                merge_target = rectangles.pop(i)
                new_left = min(current[0], merge_target[0])
                new_top = min(current[1], merge_target[1])
                new_right = max(current[0] + current[2], merge_target[0] + merge_target[2])
                new_bottom = max(current[1] + current[3], merge_target[1] + merge_target[3])
                current = [new_left, new_top, new_right - new_left, new_bottom - new_top]
                merged[-1] = current
            else:
                i += 1
    return merged

# 加载JSON数据
with open('./coordinates.json', 'r') as f:
    data = json.load(f)

# 加载图片
image_path = './example2.jpeg'  # 请替换为您的图片路径
image = cv2.imread(image_path)

# 收集所有矩形
rectangles = []
for word in data['words_result']:
    loc = word['location']
    rectangles.append([loc['left'], loc['top'], loc['width'], loc['height']])

# 合并矩形
merged_rectangles = merge_rectangles(rectangles)

# 在图片上绘制合并后的矩形
for rect in merged_rectangles:
    left, top, width, height = rect
    cv2.rectangle(image, (left, top), (left + width, top + height), (0, 0, 255), 1)

# 保存结果图片
cv2.imwrite('./output_image_merged.jpg', image)

print("处理完成，结果已保存为 'output_image_merged.jpg'")