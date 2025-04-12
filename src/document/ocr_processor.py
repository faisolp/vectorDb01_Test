"""
OCR Processor Module using EasyOCR for handling PDF documents
"""
import os
import re
import time
import numpy as np
import easyocr
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
from src.config import OCR_DPI, OCR_LANG

class OCRProcessor:
    """
    คลาสสำหรับแปลงไฟล์ PDF เป็นข้อความด้วย EasyOCR
    """
    def __init__(self, lang=None, config=None,gpu=False):
        """
        สร้าง instance ของ OCRProcessor ด้วย EasyOCR
        
        Args:
            lang (str): ภาษาที่ใช้ในการ OCR (th สำหรับภาษาไทย, en สำหรับภาษาอังกฤษ, หรือ ["th", "en"] สำหรับทั้งสองภาษา)
            config (str): ไม่ใช้ใน EasyOCR (มีไว้เพื่อความเข้ากันได้กับโค้ดเดิม)
        """
        # แปลงภาษาจากรูปแบบ Tesseract เป็น EasyOCR
        self.langs = []
        if lang is None:
            lang = OCR_LANG
            
        # แปลงรูปแบบภาษาจาก Tesseract เป็น EasyOCR
        if isinstance(lang, str):
            if "+" in lang:  # เช่น "tha+eng"
                lang_parts = lang.split("+")
                for part in lang_parts:
                    if part == "tha":
                        self.langs.append("th")
                    elif part == "eng":
                        self.langs.append("en")
            else:  # เช่น "tha" หรือ "eng"
                if lang == "tha":
                    self.langs.append("th")
                elif lang == "eng":
                    self.langs.append("en")
        
        # ถ้าไม่มีภาษาที่กำหนด ใช้ภาษาไทยและอังกฤษเป็นค่าเริ่มต้น
        if not self.langs:
            self.langs = ["th", "en"]
            
        # สร้าง EasyOCR Reader
        try:
            print(f"กำลังโหลด EasyOCR สำหรับภาษา: {', '.join(self.langs)}")
            self.reader = easyocr.Reader(self.langs, gpu=gpu)
            print(f"โหลด EasyOCR เรียบร้อยแล้ว")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการโหลด EasyOCR: {e}")
            print("โปรดติดตั้ง EasyOCR: pip install easyocr")
            raise
    
    def process_pdf(self, pdf_path, dpi=None):
        """
        แปลงไฟล์ PDF เป็นข้อความด้วย EasyOCR
        
        Args:
            pdf_path (str): พาธของไฟล์ PDF
            dpi (int): ความละเอียดของรูปภาพที่แปลงจาก PDF
            
        Returns:
            str: ข้อความที่ได้จากการ OCR
        """
        if dpi is None:
            dpi = OCR_DPI  # ใช้ค่าที่กำหนดในไฟล์ config
            
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"ไม่พบไฟล์: {pdf_path}")
        
        print(f"กำลังแปลง PDF เป็นรูปภาพ (DPI={dpi}): {pdf_path}")
        try:
            # แปลง PDF เป็นรูปภาพด้วยความละเอียดสูง
            images = convert_from_path(pdf_path, dpi=dpi)
            print(f"แปลง PDF เป็นรูปภาพสำเร็จ: ได้ {len(images)} หน้า")
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการแปลง PDF เป็นรูปภาพ: {e}")
            print("อาจต้องติดตั้ง poppler สำหรับ pdf2image: brew install poppler")
            raise
        
        text_content = []
        has_thai_characters = False
        
        print(f"กำลังประมวลผล OCR {len(images)} หน้า...")
        for i, image in enumerate(images):
            print(f"กำลังประมวลผล OCR หน้า {i+1}/{len(images)}")
            try:
                start_time = time.time()  # เริ่มจับเวลา
                
                # ปรับปรุงคุณภาพรูปภาพ
                img = self._preprocess_image(image)
                
                print(f"  กำลังทำ OCR: หน้า {i+1} (ภาษา={', '.join(self.langs)})")
                
                # ทำ OCR ด้วย EasyOCR
                results = self.reader.readtext(np.array(img))
                
                # รวมผลลัพธ์จาก EasyOCR
                page_text = ""
                for bbox, text, prob in results:
                    page_text += text + " "
                
                # ตรวจสอบว่ามีตัวอักษรภาษาไทยหรือไม่
                if re.search(r'[\u0E00-\u0E7F]', page_text):
                    has_thai_characters = True
                    print("  ✅ พบตัวอักษรภาษาไทยในผลลัพธ์ OCR")
                elif 'th' in self.langs:
                    print("  ⚠️ ไม่พบตัวอักษรภาษาไทยในผลลัพธ์ OCR แม้จะระบุภาษาไทย")
                
                # วัดเวลาที่ใช้
                process_time = time.time() - start_time
                print(f"  ใช้เวลา OCR: {process_time:.2f} วินาที")
                
                # ตรวจสอบผลลัพธ์เบื้องต้น
                if len(page_text.strip()) < 10:
                    print("  ⚠️ ผลลัพธ์ OCR มีข้อความน้อยเกินไป อาจเกิดปัญหา")
                    
                text_content.append(page_text)
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการ OCR หน้า {i+1}: {e}")
                text_content.append("")  # เพิ่มข้อความว่างถ้าเกิดข้อผิดพลาด
        
        # รวมข้อความจากทุกหน้า
        full_text = "\n\n".join(text_content)
        
        # ทำความสะอาดข้อความ
        print("กำลังทำความสะอาดข้อความ...")
        clean_text = self._clean_text(full_text)
        
        # เช็คคุณภาพของผลลัพธ์
        if 'th' in self.langs and not has_thai_characters:
            print("⚠️ คำเตือน: ไม่พบตัวอักษรภาษาไทยในผลลัพธ์ OCR แม้จะกำหนดให้รู้จำภาษาไทย")
            print("อาจเกิดจากสาเหตุดังนี้:")
            print("1. ไม่มีข้อความภาษาไทยในเอกสาร")
            print("2. รูปภาพมีคุณภาพต่ำเกินไป ไม่สามารถรู้จำตัวอักษรไทยได้")
        
        # แสดงตัวอย่างข้อความที่ได้จาก OCR
        preview_length = min(500, len(clean_text))
        print(f"\n✅ ตัวอย่างข้อความที่ได้จาก OCR ({preview_length} ตัวอักษร):")
        print(clean_text[:preview_length] + "...")
        
        # แสดงสถิติ
        total_chars = len(clean_text)
        thai_chars = len(re.findall(r'[\u0E00-\u0E7F]', clean_text))
        thai_percentage = (thai_chars / total_chars * 100) if total_chars > 0 else 0
        
        print(f"\nสถิติ OCR:")
        print(f"- จำนวนตัวอักษรทั้งหมด: {total_chars}")
        print(f"- จำนวนตัวอักษรภาษาไทย: {thai_chars} ({thai_percentage:.1f}%)")
        
        return clean_text
    
    def _preprocess_image(self, image):
        """
        ปรับปรุงคุณภาพรูปภาพก่อนทำ OCR
        
        Args:
            image (PIL.Image): รูปภาพที่ต้องการปรับปรุง
            
        Returns:
            PIL.Image: รูปภาพที่ปรับปรุงแล้ว
        """
        # แปลงเป็นภาพสีขาวดำ (grayscale)
        img = image.convert('L')
        
        # สำหรับภาษาไทยโดยเฉพาะ
        if "th" in self.langs:
            # เพิ่มความคมชัด (contrast)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)  # เพิ่มความคมชัด 2 เท่า
            
            # ปรับให้เส้นตัวอักษรชัดเจนขึ้น
            img = img.filter(ImageFilter.EDGE_ENHANCE)
        else:
            # สำหรับภาษาอื่น ใช้การปรับแต่งภาพทั่วไป
            # เพิ่มความคมชัด (contrast)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.8)  # เพิ่มความคมชัด 1.8 เท่า
            
            # เพิ่มความคมชัดของขอบ (sharpen edges)
            img = img.filter(ImageFilter.SHARPEN)
            
            # ลบ noise ด้วย median filter
            img = img.filter(ImageFilter.MedianFilter(size=3))
            
            # ปรับความสว่าง
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.2)  # เพิ่มความสว่าง 1.2 เท่า
        
        return img
    
    def _clean_text(self, text):
        """
        ทำความสะอาดข้อความที่ได้จาก OCR
        
        Args:
            text (str): ข้อความที่ได้จาก OCR
            
        Returns:
            str: ข้อความที่ทำความสะอาดแล้ว
        """
        # สำหรับภาษาไทย
        if "th" in self.langs:
            # ลบข้อความที่ไม่เกี่ยวข้องที่อาจเกิดจาก OCR
            clean_text = text
            
            # ลบเครื่องหมายพิเศษที่ไม่เกี่ยวข้องกับภาษาไทย
            clean_text = re.sub(r'[^\x20-\x7E\u0E00-\u0E7F\n]', '', clean_text)
            
            # แก้ไขปัญหาช่องว่างและบรรทัดใหม่
            clean_text = re.sub(r'\s+', ' ', clean_text)  # รวมช่องว่างหลายช่องเป็นหนึ่งช่อง
            clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)  # รวมบรรทัดว่างหลายบรรทัดเป็นสองบรรทัด
        else:
            # สำหรับภาษาอื่น ๆ
            # ลบช่องว่างซ้ำซ้อน
            clean_text = re.sub(r'\s+', ' ', text)
            
            # ลบบรรทัดว่าง
            clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
            
            # แทนที่รหัสอักขระที่ไม่ถูกต้อง
            clean_text = re.sub(r'[^\x20-\x7E\n]', '', clean_text)
        
        return clean_text