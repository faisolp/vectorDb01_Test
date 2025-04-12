"""
โปรแกรมสำหรับประมวลผลไฟล์ PDF จำนวนมากและเพิ่มลงใน Vector Database
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
from src.config import DATA_DIR, COLLECTION_NAME, MODEL_NAME, USE_OCR

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
        
        # รวบรวมไฟล์ PDF ทั้งหมดในโฟลเดอร์
        pdf_files = []
        for filename in os.listdir(DATA_DIR):
            if filename.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(DATA_DIR, filename))
        
        print(f"พบไฟล์ PDF ทั้งหมด {len(pdf_files)} ไฟล์")
        
        # ประมวลผลแต่ละไฟล์
        processed_count = 0
        for pdf_path in pdf_files:
            # ตรวจสอบว่าควรประมวลผลไฟล์นี้หรือไม่
            should_process, file_mod_time = doc_processor.should_process_file(pdf_path, collection)
            
            if should_process:
                # ประมวลผลไฟล์
                all_chunks, chunk_to_file_map, file_mod_times = doc_processor.process_file(pdf_path)
                
                # สร้าง embeddings
                print("กำลังสร้าง embeddings...")
                embeddings = []
                total_chunks = len(all_chunks)
                
                for i, chunk in enumerate(all_chunks):
                    if i % 10 == 0 or i == total_chunks - 1:
                        print(f"สร้าง embedding {i+1}/{total_chunks}")
                    embedding = model.get_embedding(chunk)
                    embeddings.append(embedding)
                    
                # เพิ่มข้อมูลลงในฐานข้อมูล
                vector_db.insert_data(chunk_to_file_map, file_mod_times, all_chunks, embeddings)
                processed_count += 1
        
        print(f"ประมวลผลเสร็จสิ้น, ไฟล์ที่ประมวลผล: {processed_count}/{len(pdf_files)}")
            
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