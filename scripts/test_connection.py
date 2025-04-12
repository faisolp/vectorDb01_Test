"""
ทดสอบการเชื่อมต่อกับ Milvus Server
"""
import os
import sys
import traceback

# เพิ่ม parent directory ไปยัง Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymilvus import connections
from src.config import MILVUS_HOST, MILVUS_PORT

def main():
    try:
        # เชื่อมต่อกับ Milvus
        print(f"กำลังเชื่อมต่อกับ Milvus ที่ {MILVUS_HOST}:{MILVUS_PORT}...")
        connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
        print("เชื่อมต่อกับ Milvus สำเร็จ!")
        
        # ตรวจสอบการเชื่อมต่อ
        if connections.has_connection("default"):
            print("การเชื่อมต่อถูกสร้างขึ้นอย่างถูกต้อง")
        else:
            print("ไม่สามารถสร้างการเชื่อมต่อได้")
            
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        # แสดงรายละเอียดข้อผิดพลาด
        traceback.print_exc()
    finally:
        # ปิดการเชื่อมต่อ
        try:
            connections.disconnect("default")
            print("ปิดการเชื่อมต่อ Milvus เรียบร้อยแล้ว")
        except:
            pass
        
        print("เสร็จสิ้น!")

if __name__ == "__main__":
    main()