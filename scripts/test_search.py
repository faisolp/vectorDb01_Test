#!/usr/bin/env python
"""
สคริปต์ทดสอบการค้นหาด้วยคำภาษาไทย
"""
import os
import sys

# เพิ่ม parent directory ไปยัง Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embedding.model import EmbeddingModel
from src.database.vector_db import VectorDatabase
from src.config import COLLECTION_NAME, MODEL_NAME, SEARCH_LIMIT

def main():
    try:
        # สร้าง embedding model
        print("กำลังโหลดโมเดล embedding...")
        model = EmbeddingModel(model_name=MODEL_NAME)
        
        # สร้างการเชื่อมต่อกับ vector database
        vector_db = VectorDatabase(
            collection_name=COLLECTION_NAME,
            dimension=model.dimension
        )
        
        # สร้างหรือโหลด collection
        collection = vector_db.create_collection()
        
        # คำค้นหาภาษาไทย (สามารถเปลี่ยนเป็นคำอื่นได้)
        thai_queries = [
            "ฐานข้อมูลเวกเตอร์คืออะไร",
            "ประโยชน์ของฐานข้อมูลเวกเตอร์",
            "Vector Database ใช้งานอย่างไร",
            "การใช้งาน Milvus",
            "เทคโนโลยีฐานข้อมูล"
        ]
        
        # ทดสอบค้นหาด้วยคำภาษาไทยทั้งหมด
        for i, query in enumerate(thai_queries):
            print(f"\n=== ค้นหาคำที่ {i+1}: '{query}' ===")
            
            # สร้าง embedding สำหรับคำค้นหา
            query_embedding = model.get_embedding(query)
            
            # ค้นหาในฐานข้อมูล
            results = vector_db.search(query_embedding, limit=SEARCH_LIMIT)
            
            # แสดงผลลัพธ์
            vector_db.display_results(results)
        
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # ปิดการเชื่อมต่อ
        if 'vector_db' in locals():
            print("กำลังปิดการเชื่อมต่อ...")
            vector_db.close()
            print("เสร็จสิ้น!")

if __name__ == "__main__":
    main()