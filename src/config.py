"""
Configuration Module for Vector Database Application
"""
import os

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "document")
PDF_PATH = os.path.join(DATA_DIR, "Vector Database.pdf")

# Database configuration
COLLECTION_NAME = "pdf_collection_thai_labse"
MILVUS_HOST = "localhost"  # หรือ "milvus-standalone" ถ้ารันในคอนเทนเนอร์ Docker เดียวกัน
MILVUS_PORT = "19530"

# Embedding model configuration
MODEL_NAME = "sentence-transformers/LaBSE"

# Document processing configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
USE_OCR = False       # ใช้ OCR สำหรับการแปลง PDF เป็นข้อความ
OCR_DPI = 800        # ความละเอียดของรูปภาพสำหรับ OCR (เพิ่มเป็น 800 เพื่อความแม่นยำในการรู้จำภาษาไทย)
OCR_LANG = "tha+eng"  # ภาษาที่ใช้ในการ OCR (tha: ภาษาไทย, eng: ภาษาอังกฤษ, tha+eng: ทั้งสองภาษา)
                      # เมื่อใช้ EasyOCR จะแปลงเป็น "th" และ "en" โดยอัตโนมัติ
OCR_CONFIG = ""       # ไม่จำเป็นต้องใช้ใน EasyOCR แต่เก็บไว้เพื่อความเข้ากันได้
OCR_GPU=True
# Search configuration
SEARCH_LIMIT = 5