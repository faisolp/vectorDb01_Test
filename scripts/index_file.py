"""
โปรแกรมหลักสำหรับการสร้างและค้นหาข้อมูลใน Vector Database
"""
import os
import sys
import time
import traceback

# เพิ่ม parent directory ไปยัง Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embedding.model import EmbeddingModel
from src.document.processor import DocumentProcessor
from src.database.vector_db import VectorDatabase
from src.config import PDF_PATH, COLLECTION_NAME, MODEL_NAME, USE_OCR

def main():
    try:
        # สร้าง embedding model
        print("กำลังโหลดโมเดล embedding...")
        model = EmbeddingModel(model_name=MODEL_NAME)
        
        # สร้าง document processor
        doc_processor = DocumentProcessor(use_ocr=USE_OCR)
        
        # สร้างการเชื่อมต่อกับ vector database
        vector_db = VectorDatabase(
            collection_name=COLLECTION_NAME,
            dimension=model.dimension
        )
        
        # สร้างหรือโหลด collection
        collection = vector_db.create_collection()
        
        # ตรวจสอบว่าควรประมวลผลไฟล์นี้หรือไม่
        should_process, file_mod_time = doc_processor.should_process_file(PDF_PATH, collection)
        
        if should_process:
            # ประมวลผลไฟล์
            all_chunks, chunk_to_file_map, file_mod_times = doc_processor.process_file(PDF_PATH)
            
            # สร้าง embeddings
            print("กำลังสร้าง embeddings...")
            embeddings = []
            for i, chunk in enumerate(all_chunks):
                if i % 10 == 0:
                    print(f"สร้าง embedding {i}/{len(all_chunks)}")
                embedding = model.get_embedding(chunk)
                embeddings.append(embedding)
                
            # เพิ่มข้อมูลลงในฐานข้อมูล
            vector_db.insert_data(chunk_to_file_map, file_mod_times, all_chunks, embeddings)
            
            # ทดสอบค้นหา
            query_text = "ฐานข้อมูลเวกเตอร์คืออะไร"  # ตัวอย่างคำถามภาษาไทย
            print(f"กำลังค้นหา: '{query_text}'")
            query_embedding = model.get_embedding(query_text)
            
            results = vector_db.search(query_embedding)
            vector_db.display_results(results)
        else:
            print("ไม่มีไฟล์ที่ต้องประมวลผลใหม่")
            
            # ถ้าผู้ใช้ต้องการค้นหา สามารถเปิดใช้งานส่วนนี้
            should_search = input("ต้องการค้นหาหรือไม่? (y/n): ").strip().lower()
            if should_search == 'y':
                query_text = input("กรอกคำค้น: ")
                print(f"กำลังค้นหา: '{query_text}'")
                query_embedding = model.get_embedding(query_text)
                
                results = vector_db.search(query_embedding)
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