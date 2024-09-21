import cv2
import numpy as np
import pytesseract
from PIL import Image
import argparse

def find_white_regions(image, min_area=1000):
    # 转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 二值化
    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
    
    # 查找轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 筛选大于最小面积的白色区域
    white_regions = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_area:
            x, y, w, h = cv2.boundingRect(contour)
            white_regions.append((x, y, w, h))
    
    return white_regions

def find_text_boundary(roi):
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x_min, y_min = roi.shape[1], roi.shape[0]
        x_max, y_max = 0, 0
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            x_max = max(x_max, x + w)
            y_max = max(y_max, y + h)
        return (x_min, y_min, x_max - x_min, y_max - y_min)
    return None

def perform_ocr(image):
    text = pytesseract.image_to_string(Image.fromarray(image))
    return text.strip()

def detect_speech_bubbles(image_path, debug=False):
    image = cv2.imread(image_path)
    white_regions = find_white_regions(image)
    
    bubbles = []
    debug_image_white = image.copy() if debug else None
    debug_image_text = image.copy() if debug else None
    
    print("检测到的白色区域:")
    for i, (x, y, w, h) in enumerate(white_regions):
        print(f"白色区域 {i+1}: 左上角 ({x}, {y}), 宽度 {w}, 高度 {h}")
        if debug:
            cv2.rectangle(debug_image_white, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        roi = image[y:y+h, x:x+w]
        text_boundary = find_text_boundary(roi)
        if text_boundary:
            tx, ty, tw, th = text_boundary
            print(f"  文本边界: 相对坐标 ({tx}, {ty}), 宽度 {tw}, 高度 {th}")
            text_roi = roi[ty:ty+th, tx:tx+tw]
            text = perform_ocr(text_roi)
            if text:
                global_x, global_y = x + tx, y + ty
                bubbles.append((text, (global_x, global_y, tw, th)))
                print(f"  全局坐标: ({global_x}, {global_y})")
                if debug:
                    cv2.rectangle(debug_image_text, (global_x, global_y), (global_x+tw, global_y+th), (0, 0, 255), 2)
        print("---")
    
    if debug:
        cv2.imwrite('detected_white_regions.jpg', debug_image_white)
        cv2.imwrite('detected_text_regions.jpg', debug_image_text)
        print("检测到的白色区域已保存为 'detected_white_regions.jpg'")
        print("检测到的文本区域已保存为 'detected_text_regions.jpg'")
    
    return bubbles

def main():
    parser = argparse.ArgumentParser(description='检测漫画图片中的对话气泡')
    parser.add_argument('image_path', type=str, help='输入图片的路径')
    parser.add_argument('--debug', action='store_true', help='启用调试模式,输出标记后的图片')
    
    args = parser.parse_args()
    
    bubbles = detect_speech_bubbles(args.image_path, args.debug)
    
    print(f"\n最终检测到 {len(bubbles)} 个文本区域:")
    for i, (text, (x, y, w, h)) in enumerate(bubbles, 1):
        print(f"区域 {i}:")
        print(f"位置: 左上角 ({x}, {y}), 宽度 {w}, 高度 {h}")
        print(f"文本: {text}")
        print("---")

if __name__ == "__main__":
    main()
