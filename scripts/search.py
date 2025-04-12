"""
โปรแกรมสำหรับการค้นหาข้อมูลใน Vector Database
"""
import os
import sys
import traceback

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
        
        print("\n=== ระบบค้นหาเอกสาร ===")
        print("พิมพ์คำค้นเพื่อค้นหาในฐานข้อมูลเวกเตอร์")
        print("พิมพ์ 'exit' เพื่อออกจากโปรแกรม")
        
        # วนลูปสำหรับการค้นหาหลายครั้ง
        while True:
            query_text = input("\nกรอกคำค้น (หรือพิมพ์ 'exit' เพื่อออก): ")
            
            if query_text.lower() == 'exit':
                break
                
            print(f"กำลังค้นหา: '{query_text}'")
            query_embedding = model.get_embedding(query_text)
            
            results = vector_db.search(query_embedding, limit=SEARCH_LIMIT)
            vector_db.display_results(results)
            
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        # แสดงรายละเอียดข้อผิดพลาด
        traceback.print_exc()
    finally:
        # ปิดการเชื่อมต่อ
        if 'vector_db' in locals():
            vector_db.close()

if __name__ == "__main__":
    main()