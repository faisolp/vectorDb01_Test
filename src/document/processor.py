"""
โมดูลสำหรับการประมวลผลเอกสาร
"""
import os
import datetime
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    """
    คลาสสำหรับการประมวลผลเอกสาร PDF
    """
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        """
        สร้าง instance ของ DocumentProcessor
        
        Args:
            chunk_size (int): ขนาดของข้อความแต่ละส่วน
            chunk_overlap (int): จำนวนตัวอักษรที่ซ้อนกันในแต่ละส่วน
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def should_process_file(self, file_path, collection):
        """
        ตรวจสอบว่าไฟล์มีการแก้ไขหรือไม่
        
        Args:
            file_path (str): พาธของไฟล์ที่ต้องการตรวจสอบ
            collection: Milvus collection สำหรับเช็คข้อมูลที่มีอยู่แล้ว
            
        Returns:
            tuple: (bool, float) - ควรประมวลผลหรือไม่, เวลาที่แก้ไขล่าสุด
        """
        # หากไฟล์ไม่มีอยู่ให้ข้าม
        if not os.path.exists(file_path):
            return False, None
        
        # รับเวลาที่ไฟล์ถูกแก้ไขล่าสุด
        file_mod_time = os.path.getmtime(file_path)
        file_mod_datetime = datetime.datetime.fromtimestamp(file_mod_time)
        file_name = os.path.basename(file_path)
        
        # ตรวจสอบว่าไฟล์นี้มีในฐานข้อมูลหรือไม่
        res = collection.query(
            expr=f'file_name == "{file_name}"',
            output_fields=["file_mod_time"]
        )
        
        # ไม่มีข้อมูลในฐานข้อมูล ต้องทำการเพิ่ม
        if len(res) == 0:
            print(f"ไฟล์ {file_name} ยังไม่มีในฐานข้อมูล จะทำการเพิ่ม")
            return True, file_mod_time
        
        # มีข้อมูลในฐานข้อมูลแล้ว ตรวจสอบเวลาแก้ไข
        db_mod_time = res[0].get("file_mod_time", 0)
        if file_mod_time > db_mod_time:
            print(f"ไฟล์ {file_name} มีการแก้ไขใหม่ จะทำการอัปเดต")
            
            # ลบข้อมูลเก่าออกก่อน
            collection.delete(expr=f'file_name == "{file_name}"')
            collection.flush()
            return True, file_mod_time
        else:
            print(f"ไฟล์ {file_name} ไม่มีการเปลี่ยนแปลง ข้ามไป")
            return False, None
    
    def process_file(self, file_path):
        """
        ประมวลผลไฟล์ PDF เพื่อแยกเป็นข้อความย่อย
        
        Args:
            file_path (str): พาธของไฟล์ PDF
            
        Returns:
            tuple: (list, list, float) - ข้อความย่อย, ชื่อไฟล์ของแต่ละส่วน, เวลาที่แก้ไขล่าสุด
        """
        file_name = os.path.basename(file_path)
        file_mod_time = os.path.getmtime(file_path)
        
        print(f"กำลังโหลดไฟล์: {file_path}")
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        text = " ".join([page.page_content for page in pages])
        
        # แบ่งเอกสารเป็นส่วนย่อย
        chunks = self.text_splitter.split_text(text)
        chunk_to_file_map = [file_name] * len(chunks)
        file_mod_times = [file_mod_time] * len(chunks)
        
        print(f"แบ่งเอกสารเป็น {len(chunks)} ส่วนย่อย")
        return chunks, chunk_to_file_map, file_mod_times