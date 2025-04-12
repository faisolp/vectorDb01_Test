#!/usr/bin/env python
"""
สคริปต์ตั้งค่า OCR และติดตั้งแพคเกจที่จำเป็น
"""
import os
import sys
import subprocess
import platform

def check_easyocr_install():
    """ตรวจสอบว่าติดตั้ง EasyOCR แล้วหรือไม่"""
    try:
        subprocess.run([sys.executable, '-c', 'import easyocr'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True, 
                        check=True)
        print(f"✅ พบ EasyOCR")
        return True
    except:
        print("❌ ไม่พบ EasyOCR")
        return False

def check_easyocr_languages():
    """ตรวจสอบภาษาที่มีใน EasyOCR"""
    try:
        subprocess.run([sys.executable, '-c', 'import easyocr; reader = easyocr.Reader(["th","en"])'], 
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE, 
                        text=True)
        print(f"✅ ภาษาไทยและภาษาอังกฤษพร้อมใช้งานใน EasyOCR")
        return True
    except:
        print("❌ เกิดปัญหาในการโหลดภาษาไทยหรือภาษาอังกฤษใน EasyOCR")
        return False

def install_easyocr():
    """ติดตั้ง EasyOCR"""
    print("กำลังติดตั้ง EasyOCR...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'easyocr'])
        print("✅ ติดตั้ง EasyOCR สำเร็จ")
        return True
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการติดตั้ง EasyOCR: {e}")
        return False

def install_tika():
    """ติดตั้ง Apache Tika"""
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'tika'])
        print("✅ ติดตั้ง tika สำเร็จ")
        
        # ตรวจสอบว่า Java ติดตั้งแล้วหรือไม่ (จำเป็นสำหรับ Tika)
        try:
            result = subprocess.run(['java', '-version'], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
            if result.returncode == 0:
                print("✅ พบ Java (จำเป็นสำหรับ Tika)")
            else:
                print("⚠️ ไม่พบ Java โปรดติดตั้ง Java Runtime Environment (JRE)")
                install_java()
        except:
            print("⚠️ ไม่พบ Java โปรดติดตั้ง Java Runtime Environment (JRE)")
            install_java()
            
        return True
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการติดตั้ง tika: {e}")
        return False

def install_java():
    """ติดตั้ง Java Runtime Environment"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("กำลังติดตั้ง Java สำหรับ macOS...")
        subprocess.run(['brew', 'install', 'openjdk'])
    elif system == "Linux":
        print("กำลังติดตั้ง Java สำหรับ Linux...")
        subprocess.run(['sudo', 'apt-get', 'update'])
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'default-jre'])
    elif system == "Windows":
        print("สำหรับ Windows กรุณาติดตั้ง Java ด้วยตนเอง:")
        print("1. ดาวน์โหลดจาก: https://www.java.com/download/")
    else:
        print(f"ไม่รองรับระบบปฏิบัติการ: {system}")
        return False

def install_other_packages():
    """ติดตั้งแพคเกจอื่นๆ ที่จำเป็น"""
    packages = ['pdf2image', 'pillow']
    
    for package in packages:
        try:
            print(f"กำลังติดตั้ง {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ ติดตั้ง {package} สำเร็จ")
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการติดตั้ง {package}: {e}")

def install_poppler():
    """ติดตั้ง Poppler (จำเป็นสำหรับ pdf2image)"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("กำลังติดตั้ง Poppler สำหรับ macOS...")
        subprocess.run(['brew', 'install', 'poppler'])
    elif system == "Linux":
        print("กำลังติดตั้ง Poppler สำหรับ Linux...")
        subprocess.run(['sudo', 'apt-get', 'update'])
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'poppler-utils'])
    elif system == "Windows":
        print("สำหรับ Windows กรุณาติดตั้ง Poppler ด้วยตนเอง:")
        print("1. ดาวน์โหลดจาก: http://blog.alivate.com.au/poppler-windows/")
        print("2. แตกไฟล์และเพิ่ม path ไปยัง environment variables")
    else:
        print(f"ไม่รองรับระบบปฏิบัติการ: {system}")

def check_environment():
    """ตรวจสอบสภาพแวดล้อมทั้งหมด"""
    print("\n=== ตรวจสอบสภาพแวดล้อมสำหรับ OCR ===")
    
    # ตรวจสอบ EasyOCR
    easyocr_installed = check_easyocr_install()
    
    # ตรวจสอบภาษาของ EasyOCR
    if easyocr_installed:
        check_easyocr_languages()
    
    # ตรวจสอบ Java (สำหรับ Tika)
    try:
        result = subprocess.run(['java', '-version'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("✅ พบ Java (จำเป็นสำหรับ Tika)")
        else:
            print("❌ ไม่พบ Java (จำเป็นสำหรับ Tika)")
    except:
        print("❌ ไม่พบ Java (จำเป็นสำหรับ Tika)")
    
    # ตรวจสอบแพคเกจ Python
    print("\nกำลังตรวจสอบแพคเกจ Python...")
    packages = ['tika', 'easyocr', 'pdf2image', 'pillow']
    
    for package in packages:
        try:
            __import__(package)
            print(f"✅ พบแพคเกจ {package}")
        except ImportError:
            print(f"❌ ไม่พบแพคเกจ {package}")

def main():
    """ฟังก์ชันหลัก"""
    print("=== โปรแกรมติดตั้ง OCR และ Tika สำหรับระบบสืบค้นข้อมูลภาษาไทย ===")
    
    # ตรวจสอบสภาพแวดล้อมก่อน
    check_environment()
    
    # ถามผู้ใช้ว่าต้องการติดตั้งหรือไม่
    choice = input("\nต้องการติดตั้งแพคเกจที่จำเป็นหรือไม่? (y/n): ").lower()
    
    if choice == 'y':
        # ติดตั้ง EasyOCR
        if not check_easyocr_install():
            install_easyocr()
        
        # ติดตั้ง Tika
        install_tika()
        
        # ติดตั้งแพคเกจอื่นๆ
        install_other_packages()
        
        # ติดตั้ง Poppler
        install_poppler()
        
        # ตรวจสอบอีกครั้งหลังติดตั้ง
        print("\n=== ตรวจสอบหลังการติดตั้ง ===")
        check_environment()
        
        print("\n✅ การติดตั้งเสร็จสิ้น")
    else:
        print("\nยกเลิกการติดตั้ง")
    
    print("\nคุณสามารถทดสอบ OCR ภาษาไทยด้วยการรันสคริปต์ index_file.py")

if __name__ == "__main__":
    main()