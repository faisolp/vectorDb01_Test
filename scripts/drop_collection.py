"""
โปรแกรมสำหรับลบ collection ใน Vector Database
"""
import os
import sys
import traceback

# เพิ่ม parent directory ไปยัง Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymilvus import connections, utility
from src.config import COLLECTION_NAME, MILVUS_HOST, MILVUS_PORT

def main():
    try:
        # เชื่อมต่อกับ Milvus
        print("กำลังเชื่อมต่อกับ Milvus...")
        connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
        
        # ตรวจสอบและรับยืนยันจากผู้ใช้
        confirm = input(f"ต้องการลบ collection '{COLLECTION_NAME}' ใช่หรือไม่? (y/n): ").strip().lower()
        
        if confirm == 'y':
            # ลบ collection
            if utility.has_collection(COLLECTION_NAME):
                print(f"กำลังลบ collection: {COLLECTION_NAME}")
                utility.drop_collection(COLLECTION_NAME)
                print(f"ลบ collection {COLLECTION_NAME} เรียบร้อยแล้ว")
            else:
                print(f"ไม่พบ collection: {COLLECTION_NAME}")
        else:
            print("ยกเลิกการลบ collection")
            
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