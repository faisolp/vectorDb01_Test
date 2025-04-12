# Vector Database Application

แอปพลิเคชันสำหรับสร้างฐานข้อมูลเวกเตอร์จากไฟล์ PDF และค้นหาข้อมูลด้วยการใช้ semantic search

## คุณสมบัติ

- แปลงเอกสาร PDF เป็น text chunks พร้อม embeddings
- ใช้ LaBSE (Language-Agnostic BERT Sentence Embedding) ซึ่งรองรับภาษาไทย
- ตรวจสอบการแก้ไขไฟล์อัตโนมัติ ไม่ประมวลผลซ้ำถ้าไฟล์ไม่มีการเปลี่ยนแปลง
- ค้นหาข้อมูลด้วย semantic search ผ่าน Milvus Vector Database

## โครงสร้างโปรเจค

```
vectorDb01/
├── document/                    # ไฟล์ PDF ที่ต้องการประมวลผล
├── docker-milvus/               # ไฟล์ Docker สำหรับ Milvus
│   ├── milvus-docker-compose.yml  # Docker Compose สำหรับ Milvus
│   └── volumes/                 # ข้อมูล Milvus
├── scripts/                     # สคริปต์สำหรับรัน
│   ├── index_file.py            # สคริปต์ประมวลผลไฟล์เดียว
│   ├── batch_index.py           # สคริปต์ประมวลผลหลายไฟล์
│   ├── search.py                # สคริปต์ค้นหาข้อมูล
│   └── drop_collection.py       # สคริปต์ลบ collection
├── src/                         # โค้ดหลัก
│   ├── embedding/               # โมดูลสำหรับ embedding
│   │   └── model.py             # คลาส EmbeddingModel
│   ├── document/                # โมดูลสำหรับประมวลผลเอกสาร
│   │   └── processor.py         # คลาส DocumentProcessor
│   ├── database/                # โมดูลสำหรับจัดการฐานข้อมูล
│   │   └── vector_db.py         # คลาส VectorDatabase
│   ├── utils/                   # โมดูลอรรถประโยชน์
│   │   └── helpers.py           # ฟังก์ชันช่วยเหลือต่างๆ
│   └── config.py                # การตั้งค่าระบบ
├── requirements.txt             # รายการ dependencies
└── README.md                    # เอกสารคำอธิบายโปรเจค
```

## การติดตั้ง

1. ติดตั้ง Python 3.8 ขึ้นไป

2. สร้าง virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # สำหรับ Linux/Mac
   # หรือ
   venv\Scripts\activate  # สำหรับ Windows
   ```

3. ติดตั้ง dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. ติดตั้ง Milvus ด้วย Docker:
   ```bash
   cd docker-milvus
   docker-compose -f milvus-docker-compose.yml up -d
   ```

## การใช้งาน

### ประมวลผลไฟล์ PDF เดี่ยว

```bash
python scripts/index_file.py
```

### ประมวลผลไฟล์ PDF หลายไฟล์

```bash
python scripts/batch_index.py
```

### ค้นหาข้อมูล

```bash
python scripts/search.py
```

### ลบ Collection

```bash
python scripts/drop_collection.py
```

## ปรับแต่งการใช้งาน

สามารถปรับแต่งการตั้งค่าได้โดยแก้ไขไฟล์ `src/config.py`:

```python
# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "document")
PDF_PATH = os.path.join(DATA_DIR, "Vector Database.pdf")

# Database configuration
COLLECTION_NAME = "pdf_collection_thai_labse"
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"

# Embedding model configuration
MODEL_NAME = "sentence-transformers/LaBSE"

# Document processing configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Search configuration
SEARCH_LIMIT = 5
```