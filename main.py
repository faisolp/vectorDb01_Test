import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import torch
import numpy as np
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility

# 1. ทางเลือกที่แนะนำคือใช้ LaBSE จาก sentence-transformers
# ซึ่งออกแบบมาสำหรับการสร้าง embedding โดยเฉพาะ และรองรับหลายภาษารวมทั้งไทย
from sentence_transformers import SentenceTransformer

# สร้าง instance ของ model
model = SentenceTransformer('sentence-transformers/LaBSE')
model.eval()

# ฟังก์ชันสำหรับสร้าง embedding
def get_embedding(text):
    embedding = model.encode(text)
    return embedding

# โหลดและเตรียม PDF
pdf_path = "/Users/faisolphalawon/data/development/vectorDb/vectorDb01/document/Vector Database.pdf"
all_chunks = []
chunk_to_file_map = []

try:
    print(f"กำลังโหลดไฟล์: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    text = " ".join([page.page_content for page in pages])
    
    # แบ่งเอกสารเป็นส่วนย่อย
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_text(text)
    all_chunks.extend(chunks)
    chunk_to_file_map.extend(["Vector Database.pdf"] * len(chunks))
    print(f"แบ่งเอกสารเป็น {len(chunks)} ส่วนย่อย")
except Exception as e:
    print(f"เกิดข้อผิดพลาดในการโหลดไฟล์ {pdf_path}: {e}")
    exit(1)

# สร้าง embeddings
print("กำลังสร้าง embeddings...")
embeddings = []
for i, chunk in enumerate(all_chunks):
    if i % 10 == 0:
        print(f"สร้าง embedding {i}/{len(all_chunks)}")
    embedding = get_embedding(chunk)
    embeddings.append(embedding)

# เชื่อมต่อกับ Milvus
print("กำลังเชื่อมต่อกับ Milvus...")
connections.connect("default", host="localhost", port="19530")
print("เชื่อมต่อกับ Milvus เรียบร้อยแล้ว")

# สร้าง collection ใน Milvus (ถ้ายังไม่มี)
collection_name = "pdf_collection_thai_labse"
dimension = 768  # ขนาด dimension ของ LaBSE

# ตรวจสอบว่า collection มีอยู่แล้วหรือไม่
if utility.has_collection(collection_name):
    print(f"ใช้ collection ที่มีอยู่แล้ว: {collection_name}")
    collection = Collection(name=collection_name)
else:
    print(f"สร้าง collection ใหม่: {collection_name}")
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="text_chunk", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension)
    ]
    schema = CollectionSchema(fields=fields, description="PDF Documents with LaBSE Embeddings")
    collection = Collection(name=collection_name, schema=schema)
    
    # สร้าง index
    print("กำลังสร้าง index...")
    index_params = {
        "metric_type": "COSINE",  # หรือใช้ "L2" ขึ้นอยู่กับความต้องการ
        "index_type": "HNSW",
        "params": {"M": 16, "efConstruction": 200}
    }
    collection.create_index(field_name="embedding", index_params=index_params)

# เปิดใช้งาน collection
print("กำลังโหลด collection...")
collection.load()

# เตรียมข้อมูลสำหรับ insert
entities = [
    chunk_to_file_map,  # file_name
    all_chunks,  # text_chunk
    embeddings  # embedding
]

# เพิ่มข้อมูล
print(f"กำลังเพิ่มข้อมูล {len(all_chunks)} chunks...")
collection.insert(entities)
collection.flush()  # ยืนยันว่าข้อมูลถูกบันทึก
print("เพิ่มข้อมูลเรียบร้อยแล้ว")

# ตัวอย่างการค้นหา
query_text = "ฐานข้อมูลเวกเตอร์คืออะไร"  # ตัวอย่างคำถามภาษาไทย
print(f"กำลังค้นหา: '{query_text}'")
query_embedding = get_embedding(query_text)

search_params = {
    "metric_type": "COSINE",
    "params": {"ef": 100}
}

results = collection.search(
    data=[query_embedding],
    anns_field="embedding",
    param=search_params,
    limit=5,
    output_fields=["file_name", "text_chunk"]
)

# แสดงผลลัพธ์
print("\nผลลัพธ์การค้นหา:")
for hits in results:
    for hit in hits:
        print(f"Score: {hit.score}")
        print(f"File: {hit.entity.get('file_name')}")
        print(f"Text Chunk: {hit.entity.get('text_chunk')}")
        print("----------------------------")

# ปิดการเชื่อมต่อ
print("กำลังปิดการเชื่อมต่อ...")
connections.disconnect("default")
print("เสร็จสิ้น!")