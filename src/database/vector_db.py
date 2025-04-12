"""
โมดูลสำหรับการจัดการฐานข้อมูลเวกเตอร์
"""
import datetime
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility

class VectorDatabase:
    """
    คลาสสำหรับการจัดการฐานข้อมูลเวกเตอร์ (Milvus)
    """
    def __init__(self, collection_name, dimension, host="localhost", port="19530"):
        """
        สร้าง instance ของ VectorDatabase
        
        Args:
            collection_name (str): ชื่อของ collection ใน Milvus
            dimension (int): ขนาดของ vector embedding
            host (str): โฮสต์ของ Milvus server
            port (str): พอร์ตของ Milvus server
        """
        self.collection_name = collection_name
        self.dimension = dimension
        self.host = host
        self.port = port
        self.collection = None
        
        # เชื่อมต่อกับ Milvus
        print("กำลังเชื่อมต่อกับ Milvus...")
        connections.connect("default", host=host, port=port)
        print("เชื่อมต่อกับ Milvus เรียบร้อยแล้ว")
    
    def create_collection(self):
        """
        สร้าง collection ใน Milvus (ถ้ายังไม่มี)
        """
        # ตรวจสอบว่า collection มีอยู่แล้วหรือไม่
        if utility.has_collection(self.collection_name):
            print(f"ใช้ collection ที่มีอยู่แล้ว: {self.collection_name}")
            self.collection = Collection(name=self.collection_name)
        else:
            print(f"สร้าง collection ใหม่: {self.collection_name}")
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=256),
                FieldSchema(name="file_mod_time", dtype=DataType.DOUBLE),  # เวลาที่แก้ไขล่าสุด
                FieldSchema(name="text_chunk", dtype=DataType.VARCHAR, max_length=65535),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dimension)
            ]
            schema = CollectionSchema(fields=fields, description="PDF Documents with Embeddings")
            self.collection = Collection(name=self.collection_name, schema=schema)
            
            # สร้าง index
            print("กำลังสร้าง index...")
            index_params = {
                "metric_type": "COSINE",  # หรือใช้ "L2" ขึ้นอยู่กับความต้องการ
                "index_type": "HNSW",
                "params": {"M": 16, "efConstruction": 200}
            }
            self.collection.create_index(field_name="embedding", index_params=index_params)
        
        # เปิดใช้งาน collection
        print("กำลังโหลด collection...")
        self.collection.load()
        
        return self.collection
    
    def insert_data(self, chunk_to_file_map, file_mod_times, all_chunks, embeddings):
        """
        เพิ่มข้อมูลเข้า collection
        
        Args:
            chunk_to_file_map (list): ชื่อไฟล์ของแต่ละส่วน
            file_mod_times (list): เวลาที่แก้ไขของแต่ละไฟล์
            all_chunks (list): ข้อความย่อยทั้งหมด
            embeddings (list): embedding vectors
        """
        if not self.collection:
            raise ValueError("ยังไม่ได้สร้าง collection")
        
        # เตรียมข้อมูลสำหรับ insert
        entities = [
            chunk_to_file_map,  # file_name
            file_mod_times,     # file_mod_time
            all_chunks,         # text_chunk
            embeddings          # embedding
        ]
        
        # เพิ่มข้อมูล
        print(f"กำลังเพิ่มข้อมูล {len(all_chunks)} chunks...")
        self.collection.insert(entities)
        self.collection.flush()  # ยืนยันว่าข้อมูลถูกบันทึก
        print("เพิ่มข้อมูลเรียบร้อยแล้ว")
    
    def search(self, query_embedding, limit=5):
        """
        ค้นหาข้อมูลที่คล้ายกับ query embedding
        
        Args:
            query_embedding: embedding vector ของคำค้น
            limit (int): จำนวนผลลัพธ์ที่ต้องการ
            
        Returns:
            list: ผลลัพธ์การค้นหา
        """
        if not self.collection:
            raise ValueError("ยังไม่ได้สร้าง collection")
        
        search_params = {
            "metric_type": "COSINE",
            "params": {"ef": 100}
        }
        
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            output_fields=["file_name", "text_chunk", "file_mod_time"]
        )
        
        return results
    
    def display_results(self, results):
        """
        แสดงผลลัพธ์การค้นหา
        
        Args:
            results: ผลลัพธ์จากการค้นหา
        """
        print("\nผลลัพธ์การค้นหา:")
        for hits in results:
            for hit in hits:
                mod_time_str = datetime.datetime.fromtimestamp(hit.entity.get('file_mod_time')).strftime('%Y-%m-%d %H:%M:%S')
                print(f"Score: {hit.score}")
                print(f"File: {hit.entity.get('file_name')}")
                print(f"Modified: {mod_time_str}")
                print(f"Text Chunk: {hit.entity.get('text_chunk')}")
                print("----------------------------")
    
    def close(self):
        """
        ปิดการเชื่อมต่อกับ Milvus
        """
        print("กำลังปิดการเชื่อมต่อ...")
        connections.disconnect("default")
        print("เสร็จสิ้น!")