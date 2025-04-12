"""
OCR Processor Module for handling PDF documents
"""
import os
import re
import time
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
from src.config import OCR_DPI

class OCRProcessor:
    """
    คลาสสำหรับแปลงไฟล์ PDF เป็นข้อความด้วย OCR
    """
    def __init__(self, lang="tha", config="--psm 6 --oem 1"):
        """
        สร้าง instance ของ OCRProcessor
        
        Args:
            lang (str): ภาษาที่ใช้ในการ OCR (tha สำหรับภาษาไทย, eng สำหรับภาษาอังกฤษ, tha+eng สำหรับทั้งสองภาษา)
            config (str): การตั้งค่า Tesseract OCR
                - psm: Page segmentation modes
                  - 0: Orientation and script detection only
                  - 1: Automatic page segmentation with OSD
                  - 3: Fully automatic page segmentation, but no OSD
                  - 4: Assume a single column of text of variable sizes
                  - 6: Assume a single uniform block of text (recommended for Thai)
                  - 7: Treat the image as a single text line
                  - 11: Sparse text. Find as much text as possible in no particular order
                  - 12: Sparse text with OSD
                - oem: OCR Engine modes
                  - 0: Legacy engine only
                  - 1: Neural nets LSTM engine only (recommended for Thai)
                  - 2: Legacy + LSTM engines
                  - 3: Default, based on what is available
        """
        self.lang = lang
        self.config = config
        # ตรวจสอบว่า Tesseract ติดตั้งแล้ว
        try:
            tesseract_version = pytesseract.get_tesseract_version()
            print(f"ใช้ Tesseract OCR เวอร์ชัน: {tesseract_version}")
            print(f"ภาษาที่ใช้: {self.lang}")
            print(f"ค่าตั้งค่า OCR: {self.config}")
            
            # ตรวจสอบว่ามีภาษาที่ต้องการหรือไม่
            available_langs = pytesseract.get_languages()
            print(f"ภาษาที่ติดตั้ง: {', '.join(available_langs)}")
            
            # ตรวจสอบภาษาไทย
            if 'tha' in self.lang:
                if 'tha' not in available_langs:
                    print(f"⚠️ ไม่พบภาษาไทยในรายการภาษาที่ติดตั้ง")
                    print("กำลังติดตั้งข้อมูลภาษาไทย...")
                    print("โปรดใช้คำสั่ง: brew install tesseract-lang หรือ sudo apt-get install tesseract-ocr-tha")
                    
                    # ถ้าไม่มีภาษาไทย แต่ต้องการทั้งไทยและอังกฤษ
                    if self.lang == 'tha+eng' and 'eng' in available_langs:
                        print("ใช้ภาษาอังกฤษแทนชั่วคราว (ผลลัพธ์อาจไม่สมบูรณ์)")
                        self.lang = "eng"
                    # ถ้าต้องการเฉพาะภาษาไทย แต่ไม่มี
                    elif self.lang == 'tha':
                        print("ใช้ภาษาอังกฤษแทนชั่วคราว (ผลลัพธ์อาจไม่สมบูรณ์)")
                        if 'eng' in available_langs:
                            self.lang = "eng"
                        else:
                            raise ValueError("ไม่พบภาษาที่รองรับในระบบ กรุณาติดตั้งข้อมูลภาษาไทยหรือภาษาอังกฤษ")
                else:
                    print("✅ พบภาษาไทยในระบบ")
                    
                    # ปรับค่า config เหมาะสมกับภาษาไทย
                    if self.config == "--psm 1 --oem 1":
                        # ถ้าใช้ค่าเดิม แนะนำให้ใช้ค่าที่เหมาะกับภาษาไทยมากกว่า
                        print("ปรับค่า config เป็น --psm 6 --oem 1 สำหรับภาษาไทย (แนะนำ)")
                        self.config = "--psm 6 --oem 1"
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการตรวจสอบ Tesseract OCR: {e}")
            print("โปรดติดตั้ง Tesseract OCR: brew install tesseract tesseract-lang")
            raise
    
    def process_pdf(self, pdf_path, dpi=None):
        """
        แปลงไฟล์ PDF เป็นข้อความด้วย OCR
        
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
                
                # ปรับปรุงคุณภาพรูปภาพเพื่อเพิ่มความแม่นยำของ OCR
                img = self._preprocess_image(image)
                
                print(f"  กำลังทำ OCR: หน้า {i+1} (ภาษา={self.lang}, คอนฟิกูเรชัน={self.config})")
                
                # ทำ OCR
                text = pytesseract.image_to_string(img, lang=self.lang, config=self.config)
                
                # ตรวจสอบว่ามีตัวอักษรภาษาไทยหรือไม่
                if re.search(r'[\u0E00-\u0E7F]', text):
                    has_thai_characters = True
                    print("  ✅ พบตัวอักษรภาษาไทยในผลลัพธ์ OCR")
                elif 'tha' in self.lang:
                    print("  ⚠️ ไม่พบตัวอักษรภาษาไทยในผลลัพธ์ OCR แม้จะระบุภาษาไทย")
                
                # วัดเวลาที่ใช้
                process_time = time.time() - start_time
                print(f"  ใช้เวลา OCR: {process_time:.2f} วินาที")
                
                # ตรวจสอบผลลัพธ์เบื้องต้น
                if len(text.strip()) < 10:
                    print("  ⚠️ ผลลัพธ์ OCR มีข้อความน้อยเกินไป อาจเกิดปัญหา")
                elif "Image Recognition" in text and 'tha' in self.lang:
                    print("  ⚠️ พบข้อความ 'Image Recognition' ซึ่งอาจเป็นปัญหาในการรู้จำภาษาไทย")
                    
                text_content.append(text)
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการ OCR หน้า {i+1}: {e}")
                text_content.append("")  # เพิ่มข้อความว่างถ้าเกิดข้อผิดพลาด
        
        # รวมข้อความจากทุกหน้า
        full_text = "\n\n".join(text_content)
        
        # ทำความสะอาดข้อความ
        print("กำลังทำความสะอาดข้อความ...")
        clean_text = self._clean_text(full_text)
        
        # เช็คคุณภาพของผลลัพธ์
        if 'tha' in self.lang and not has_thai_characters:
            print("⚠️ คำเตือน: ไม่พบตัวอักษรภาษาไทยในผลลัพธ์ OCR แม้จะกำหนดให้รู้จำภาษาไทย")
            print("อาจเกิดจากสาเหตุดังนี้:")
            print("1. ไม่ได้ติดตั้งข้อมูลภาษาไทยสำหรับ Tesseract")
            print("2. รูปภาพมีคุณภาพต่ำเกินไป ไม่สามารถรู้จำตัวอักษรไทยได้")
            print("3. การตั้งค่า OCR ไม่เหมาะสมกับภาษาไทย")
            print("แนะนำให้ติดตั้งข้อมูลภาษาไทยด้วยคำสั่ง: brew install tesseract-lang")
        
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
        if self.lang == 'tha' or 'tha' in self.lang:
            # เพิ่มขนาดของภาพเพื่อให้อักขระภาษาไทยชัดเจนขึ้น
            w, h = img.size
            img = img.resize((w*3, h*3), Image.LANCZOS)  # เพิ่มขนาด 3 เท่า สำหรับภาษาไทย
            
            # เพิ่มความคมชัด (contrast) มากขึ้นสำหรับภาษาไทย
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.5)  # เพิ่มความคมชัด 2.5 เท่าสำหรับภาษาไทย
            
            # ลบ noise ด้วย threshold
            # ใช้ function threshold เพื่อแบ่งแยกสีขาวกับสีดำชัดเจน
            # เหมาะสำหรับตัวอักษรภาษาไทยที่มีเส้นบางและวนโค้ง
            img = img.point(lambda x: 0 if x < 150 else 255, '1')
            
            # ปรับให้เส้นตัวอักษรชัดเจนขึ้น
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        else:
            # สำหรับภาษาอื่น ใช้การปรับแต่งภาพทั่วไป
            # เพิ่มความคมชัด (contrast)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)  # เพิ่มความคมชัด 2 เท่า
            
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
        if self.lang == 'tha' or 'tha' in self.lang:
            # ลบข้อความที่ไม่เกี่ยวข้องที่อาจเกิดจาก OCR เช่น "Image Recognition"
            clean_text = re.sub(r'Image Recognition', '', text, flags=re.IGNORECASE)
            clean_text = re.sub(r'Lanna lunisa\w*', '', clean_text, flags=re.IGNORECASE)
            clean_text = re.sub(r'tiunrauszene la vector search', '', clean_text, flags=re.IGNORECASE)
            
            # แก้ไขปัญหาช่องว่างในคำภาษาไทย
            # รวมตัวอักษรไทยที่ถูกแยกด้วยช่องว่าง
            def combine_thai_chars(match):
                return match.group(0).replace(' ', '')
            
            # จับกลุ่มตัวอักษรไทยที่มีช่องว่างคั่น และรวมเข้าด้วยกัน
            pattern = r'[\u0E00-\u0E7F]+(\s+[\u0E00-\u0E7F]+)*'
            clean_text = re.sub(pattern, combine_thai_chars, clean_text)
            
            # ลบเครื่องหมายพิเศษที่ไม่เกี่ยวข้องกับภาษาไทย
            clean_text = re.sub(r'[^\x20-\x7E\u0E00-\u0E7F\n]', '', clean_text)
            
            # แก้ไขปัญหาช่องว่างและบรรทัดใหม่
            clean_text = re.sub(r'\s+', ' ', clean_text)  # รวมช่องว่างหลายช่องเป็นหนึ่งช่อง
            clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)  # รวมบรรทัดว่างหลายบรรทัดเป็นสองบรรทัด
            
            # แก้ไขข้อความภาษาไทยที่มีปัญหา
            # แทนที่อักขระที่มักถูก OCR แปลผิด (ใ → l, ไ → 1, etc.)
            clean_text = clean_text.replace('l', 'ใ')
            clean_text = clean_text.replace('1', 'ไ')
            
            # แก้ไขสระลอย (สระที่ถูกแยกออกจากพยัญชนะ)
            vowel_patterns = [
                (r'([ก-ฮ])\s+([\u0E31-\u0E3A\u0E47-\u0E4E])', r'\1\2'),  # พยัญชนะ + ช่องว่าง + สระบน/ล่าง/วรรณยุกต์
                (r'([\u0E31-\u0E3A\u0E47-\u0E4E])\s+([ก-ฮ])', r'\1\2')   # สระบน/ล่าง/วรรณยุกต์ + ช่องว่าง + พยัญชนะ
            ]
            
            for pattern, replacement in vowel_patterns:
                clean_text = re.sub(pattern, replacement, clean_text)
        else:
            # สำหรับภาษาอื่น ๆ
            # ลบช่องว่างซ้ำซ้อน
            clean_text = re.sub(r'\s+', ' ', text)
            
            # ลบบรรทัดว่าง
            clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)
            
            # แทนที่รหัสอักขระที่ไม่ถูกต้อง
            clean_text = re.sub(r'[^\x20-\x7E\n]', '', clean_text)
        
        return clean_text