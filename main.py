import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import torch
import numpy as np
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility

# โหลดโมเดล Sentence Transformers (public model)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
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
except Exception as e:
    print(f"เกิดข้อผิดพลาดในการโหลดไฟล์ {pdf_path}: {e}")

# สร้าง embeddings
embeddings = [get_embedding(chunk) for chunk in all_chunks]

# เชื่อมต่อกับ Milvus
connections.connect("default", host="localhost", port="19530")

# สร้าง collection ใน Milvus (ถ้ายังไม่มี)
collection_name = "pdf_collection"
dimension = 384  # ขนาด dimension ของ all-MiniLM-L6-v2

# ตรวจสอบว่า collection มีอยู่แล้วหรือไม่
if utility.has_collection(collection_name):
    collection = Collection(name=collection_name)
else:
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=256),
        FieldSchema(name="text_chunk", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension)
    ]
    schema = CollectionSchema(fields=fields, description="PDF Documents with DeepSeek Embeddings")
    collection = Collection(name=collection_name, schema=schema)
    
    # สร้าง index
    index_params = {
        "metric_type": "COSINE",  # หรือใช้ "L2" ขึ้นอยู่กับความต้องการ
        "index_type": "HNSW",
        "params": {"M": 16, "efConstruction": 200}
    }
    collection.create_index(field_name="embedding", index_params=index_params)

# เตรียมข้อมูลสำหรับ insert
entities = [
    [i for i in range(len(all_chunks))],  # id จะถูกสร้างอัตโนมัติเพราะเรากำหนด auto_id=True
    chunk_to_file_map,  # file_name
    all_chunks,  # text_chunk
    embeddings  # embedding
]

# เปิดใช้งาน collection
collection.load()

# เพิ่มข้อมูล
collection.insert(entities)
collection.flush()  # ยืนยันว่าข้อมูลถูกบันทึก

# ตัวอย่างการค้นหา
query_text = "คำถามที่ต้องการค้นหา"
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
for hits in results:
    for hit in hits:
        print(f"Score: {hit.score}")
        print(f"File: {hit.entity.get('file_name')}")
        print(f"Text Chunk: {hit.entity.get('text_chunk')}")
        print("----------------------------")

# ปิดการเชื่อมต่อ
connections.disconnect("default")