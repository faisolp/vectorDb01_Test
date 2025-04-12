#!/usr/bin/env python
"""
สคริปต์ทดสอบ OCR และ Tika สำหรับภาษาไทย
"""
import os
import sys
import argparse

# เพิ่ม parent directory ไปยัง Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.document.ocr_processor import OCRProcessor
from tika import parser
from src.config import OCR_LANG, OCR_CONFIG, OCR_DPI

def test_tesseract_ocr(file_path, lang=None, config=None, dpi=None):
    """ทดสอบการทำงานของ Tesseract OCR"""
    print("\n=== ทดสอบ Tesseract OCR ===")
    
    # ใช้ค่าที่กำหนดในไฟล์ config ถ้าไม่ได้ระบุ
    if lang is None:
        lang = OCR_LANG
    if config is None:
        config = OCR_CONFIG
    if dpi is None:
        dpi = OCR_DPI
    
    try:
        # สร้าง OCR processor
        ocr = OCRProcessor(lang=lang, config=config)
        
        # ทำ OCR
        text = ocr.process_pdf(file_path, dpi=dpi)
        
        # แสดงผลลัพธ์
        print("\n=== ผลลัพธ์จาก Tesseract OCR ===")
        
        # นับจำนวนตัวอักษรไทย
        thai_chars = 0
        for char in text:
            if '\u0E00' <= char <= '\u0E7F':
                thai_chars += 1
        
        print(f"จำนวนตัวอักษรทั้งหมด: {len(text)}")
        print(f"จำนวนตัวอักษรภาษาไทย: {thai_chars}")
        if len(text) > 0:
            print(f"สัดส่วนตัวอักษรภาษาไทย: {thai_chars/len(text)*100:.2f}%")
        
        # บันทึกผลลัพธ์ลงไฟล์
        output_file = os.path.join(os.path.dirname(file_path), "ocr_output.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)
        
        print(f"บันทึกผลลัพธ์ไปยัง: {output_file}")
        
        return True
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการทำ OCR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tika_parser(file_path):
    """ทดสอบการทำงานของ Tika Parser"""
    print("\n=== ทดสอบ Tika Parser ===")
    
    try:
        # แปลงไฟล์ด้วย Tika
        print(f"กำลังแปลงไฟล์ด้วย Tika: {file_path}")
        parsed = parser.from_file(file_path)
        
        # ตรวจสอบว่ามีเนื้อหาหรือไม่
        if parsed['content']:
            text = parsed['content']
            
            # นับจำนวนตัวอักษรไทย
            thai_chars = 0
            for char in text:
                if '\u0E00' <= char <= '\u0E7F':
                    thai_chars += 1
            
            print(f"จำนวนตัวอักษรทั้งหมด: {len(text)}")
            print(f"จำนวนตัวอักษรภาษาไทย: {thai_chars}")
            if len(text) > 0:
                print(f"สัดส่วนตัวอักษรภาษาไทย: {thai_chars/len(text)*100:.2f}%")
            
            # แสดงตัวอย่างข้อความ
            preview_length = min(500, len(text))
            print("\nตัวอย่างข้อความ:")
            print(text[:preview_length] + "...")
            
            # บันทึกผลลัพธ์ลงไฟล์
            output_file = os.path.join(os.path.dirname(file_path), "tika_output.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
            
            print(f"บันทึกผลลัพธ์ไปยัง: {output_file}")
            
            return True
        else:
            print("ไม่พบเนื้อหาในไฟล์หรือ Tika ไม่สามารถประมวลผลได้")
            return False
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการใช้ Tika: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """ฟังก์ชันหลัก"""
    parser = argparse.ArgumentParser(description="ทดสอบ OCR และ Tika สำหรับภาษาไทย")
    parser.add_argument("file_path", help="พาธของไฟล์ PDF ที่ต้องการทดสอบ")
    parser.add_argument("--ocr-only", action="store_true", help="ทดสอบเฉพาะ OCR")
    parser.add_argument("--tika-only", action="store_true", help="ทดสอบเฉพาะ Tika")
    parser.add_argument("--lang", help=f"ภาษาที่ใช้ใน OCR (ค่าเริ่มต้น: {OCR_LANG})")
    parser.add_argument("--config", help=f"การตั้งค่า OCR (ค่าเริ่มต้น: {OCR_CONFIG})")
    parser.add_argument("--dpi", type=int, help=f"ความละเอียด DPI (ค่าเริ่มต้น: {OCR_DPI})")
    
    args = parser.parse_args()
    
    # ตรวจสอบว่าไฟล์มีอยู่หรือไม่
    if not os.path.exists(args.file_path):
        print(f"ไม่พบไฟล์: {args.file_path}")
        return
    
    # ตรวจสอบนามสกุลไฟล์
    if not args.file_path.lower().endswith(".pdf"):
        print("ไฟล์ต้องเป็นรูปแบบ PDF เท่านั้น")
        return
    
    print(f"กำลังทดสอบไฟล์: {args.file_path}")
    
    # ทดสอบตามที่กำหนด
    if args.ocr_only:
        test_tesseract_ocr(args.file_path, args.lang, args.config, args.dpi)
    elif args.tika_only:
        test_tika_parser(args.file_path)
    else:
        # ทดสอบทั้ง OCR และ Tika
        test_tesseract_ocr(args.file_path, args.lang, args.config, args.dpi)
        test_tika_parser(args.file_path)
    
    print("\nการทดสอบเสร็จสิ้น")

if __name__ == "__main__":
    main()