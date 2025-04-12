"""
โมดูลรวมฟังก์ชั่นอรรถประโยชน์ต่างๆ
"""
import os
import datetime
import json

def format_time(timestamp):
    """
    แปลงเวลาในรูปแบบ timestamp เป็นสตริง
    
    Args:
        timestamp (float): เวลาในรูปแบบ timestamp
        
    Returns:
        str: เวลาในรูปแบบสตริง
    """
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def get_file_info(file_path):
    """
    ดึงข้อมูลต่างๆ ของไฟล์
    
    Args:
        file_path (str): พาธของไฟล์
        
    Returns:
        dict: ข้อมูลของไฟล์
    """
    if not os.path.exists(file_path):
        return None
    
    stats = os.stat(file_path)
    
    info = {
        'name': os.path.basename(file_path),
        'path': file_path,
        'size': stats.st_size,
        'size_human': format_size(stats.st_size),
        'created': format_time(stats.st_ctime),
        'modified': format_time(stats.st_mtime),
        'accessed': format_time(stats.st_atime),
    }
    
    return info

def format_size(size_bytes):
    """
    แปลงขนาดไฟล์จาก bytes เป็นหน่วยที่อ่านง่าย
    
    Args:
        size_bytes (int): ขนาดไฟล์ในหน่วย bytes
        
    Returns:
        str: ขนาดไฟล์ในหน่วยที่อ่านง่าย
    """
    # ขนาดหน่วย
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024
        i += 1
        
    return f"{size_bytes:.2f} {size_name[i]}"

def save_json(data, file_path):
    """
    บันทึกข้อมูลลงในไฟล์ JSON
    
    Args:
        data: ข้อมูลที่ต้องการบันทึก
        file_path (str): พาธของไฟล์ที่ต้องการบันทึก
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
def load_json(file_path):
    """
    โหลดข้อมูลจากไฟล์ JSON
    
    Args:
        file_path (str): พาธของไฟล์ที่ต้องการโหลด
        
    Returns:
        dict: ข้อมูลที่โหลดจากไฟล์
    """
    if not os.path.exists(file_path):
        return None
        
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)