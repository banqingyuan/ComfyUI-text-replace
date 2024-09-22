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

# 对矩形进行排序（从左上到右下）
merged_rectangles.sort(key=lambda r: (r[1], r[0]))

# 在图片上绘制合并后的矩形和序号
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
font_thickness = 1
padding = 2

for i, rect in enumerate(merged_rectangles, 1):
    left, top, width, height = rect
    cv2.rectangle(image, (left, top), (left + width, top + height), (0, 0, 255), 1)
    
    # 确定序号的位置
    label = str(i)
    (label_width, label_height), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
    
    # 尝试将序号放在左上角
    label_x = max(left, padding)
    label_y = max(top - padding, label_height + padding)
    
    # 如果左上角放不下，尝试右上角
    if label_x + label_width > left + width or label_y - label_height < top:
        label_x = min(left + width - label_width - padding, image.shape[1] - label_width - padding)
        label_y = max(top - padding, label_height + padding)
    
    # 如果右上角也放不下，放在左下角
    if label_y - label_height < top:
        label_y = min(top + height + label_height + padding, image.shape[0] - padding)
    
    # 绘制白色背景
    cv2.rectangle(image, (label_x - padding, label_y - label_height - padding),
                  (label_x + label_width + padding, label_y + padding), (255, 255, 255), -1)
    
    # 绘制序号
    cv2.putText(image, label, (label_x, label_y), font, font_scale, (0, 0, 255), font_thickness)

# 保存结果图片
cv2.imwrite('./output_image_numbered.jpg', image)

print("处理完成，结果已保存为 'output_image_numbered.jpg'")