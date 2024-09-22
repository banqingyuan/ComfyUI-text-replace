import cv2
import numpy as np

def should_merge(rect1, rect2, vertical_threshold=5, overlap_threshold=0.5):
    vertical_close = abs(rect1[1] + rect1[3] - rect2[1]) <= vertical_threshold or \
                     abs(rect2[1] + rect2[3] - rect1[1]) <= vertical_threshold
    
    overlap = min(rect1[0] + rect1[2], rect2[0] + rect2[2]) - max(rect1[0], rect2[0])
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

def process_image_with_rectangles(image, rectangles):
    merged_rectangles = merge_rectangles(rectangles)
    merged_rectangles.sort(key=lambda r: (r[1], r[0]))

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7  # 增大字体大小
    font_thickness = 2  # 增加字体粗细
    padding = 3  # 增加内边距

    labeled_rectangles = []

    for i, rect in enumerate(merged_rectangles, 1):
        left, top, width, height = rect
        cv2.rectangle(image, (left, top), (left + width, top + height), (0, 0, 255), 2)  # 红色，线条加粗
        
        label = str(i)
        (label_width, label_height), _ = cv2.getTextSize(label, font, font_scale, font_thickness)
        
        # 尝试将标签放在矩形内部的右下角
        label_x = left + width - label_width - padding
        label_y = top + height - padding

        # 如果标签超出矩形范围，则调整位置
        if label_x < left + padding:
            label_x = left + padding
        if label_y - label_height < top + padding:
            label_y = top + label_height + padding

        cv2.rectangle(image, (label_x - padding, label_y - label_height - padding),
                      (label_x + label_width + padding, label_y + padding), (255, 255, 255), -1)
        
        cv2.putText(image, label, (label_x, label_y), font, font_scale, (0, 0, 255), font_thickness)

        labeled_rectangles.append({
            "id": i,
            "left": left,
            "top": top,
            "width": width,
            "height": height
        })

    return image, labeled_rectangles

