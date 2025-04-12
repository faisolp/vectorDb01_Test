"""
โมดูลสำหรับการประมวลผลเอกสาร
"""
import os
import datetime
import importlib.util
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.document.ocr_processor import OCRProcessor
from src.config import CHUNK_SIZE, CHUNK_OVERLAP, USE_OCR, OCR_LANG, OCR_CONFIG
from tika import parser as tika_parser

class DocumentProcessor:
    """
    คลาสสำหรับการประมวลผลเอกสาร PDF
    """
    def __init__(self, chunk_size=None, chunk_overlap=None, use_ocr=None, ocr_lang=None, ocr_config=None):
        """
        สร้าง instance ของ DocumentProcessor
        
        Args:
            chunk_size (int): ขนาดของข้อความแต่ละส่วน
            chunk_overlap (int): จำนวนตัวอักษรที่ซ้อนกันในแต่ละส่วน
            use_ocr (bool): ใช้ OCR หรือไม่
            ocr_lang (str): ภาษาที่ใช้ใน OCR
            ocr_config (str): การตั้งค่า OCR
        """
        # ใช้ค่าจาก config ถ้าไม่ได้ระบุ
        self.chunk_size = chunk_size if chunk_size is not None else CHUNK_SIZE
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else CHUNK_OVERLAP
        self.use_ocr = use_ocr if use_ocr is not None else USE_OCR
        self.ocr_lang = ocr_lang if ocr_lang is not None else OCR_LANG
        self.ocr_config = ocr_config if ocr_config is not None else OCR_CONFIG
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        
        if self.use_ocr:
            try:
                self.ocr_processor = OCRProcessor(lang=self.ocr_lang, config=self.ocr_config)
                print("เปิดใช้งาน OCR สำหรับการแปลงไฟล์ PDF")
            except Exception as e:
                print(f"ไม่สามารถใช้งาน OCR ได้: {e}")
                print("จะใช้วิธีการแปลงแบบปกติแทน")
                self.use_ocr = False
    
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
        
        # ใช้ OCR หรือวิธีปกติในการแปลง PDF เป็นข้อความ
        if self.use_ocr:
            text = self.ocr_processor.process_pdf(file_path)
        else:
            # ใช้ Tika parser
        
                print(f"กำลังแปลง PDF เป็นข้อความด้วย Tika parser: {file_path}")
                try:
                    parsed_pdf = tika_parser.from_file(file_path)
                    text = parsed_pdf['content'] if parsed_pdf['content'] else ""
                    if not text:
                        print("⚠️ Tika ไม่สามารถแยกข้อความจาก PDF ได้ หรือไฟล์ไม่มีข้อความ")
                        print("กรุณาลองใช้ OCR (ตั้งค่า USE_OCR = True) เพื่อแปลง PDF เป็นข้อความ")
                        text = ""
                    else:
                        preview_length = min(500, len(text))
                        print(f"Tika แยกข้อความได้ {len(text)} ตัวอักษร")
                        print(f"ตัวอย่างข้อความ: {text[:preview_length]}...")
                except Exception as e:
                    print(f"⚠️ เกิดข้อผิดพลาดในการใช้ Tika: {e}")
                    print("กรุณาลองใช้ OCR (ตั้งค่า USE_OCR = True) เพื่อแปลง PDF เป็นข้อความ")
                    text = ""
          
        
        # แบ่งเอกสารเป็นส่วนย่อย
        chunks = self.text_splitter.split_text(text)
        chunk_to_file_map = [file_name] * len(chunks)
        file_mod_times = [file_mod_time] * len(chunks)
        
        print(f"แบ่งเอกสารเป็น {len(chunks)} ส่วนย่อย")
        return chunks, chunk_to_file_map, file_mod_times