#!/usr/bin/env python
"""
สคริปต์ตั้งค่า OCR และติดตั้งแพคเกจที่จำเป็น
"""
import os
import sys
import subprocess
import platform

def check_tesseract_install():
    """ตรวจสอบว่าติดตั้ง Tesseract แล้วหรือไม่"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True)
        if result.returncode == 0:
            print(f"✅ พบ Tesseract OCR: {result.stdout.splitlines()[0]}")
            return True
        return False
    except:
        return False

def check_tesseract_languages():
    """ตรวจสอบภาษาที่ติดตั้งใน Tesseract"""
    try:
        result = subprocess.run(['tesseract', '--list-langs'], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, 
                                text=True)
        if result.returncode == 0:
            output = result.stdout if result.stdout else result.stderr
            langs = [lang.strip() for lang in output.splitlines()[1:]]
            print(f"ภาษาที่ติดตั้ง ({len(langs)}): {', '.join(langs)}")
            return langs
        return []
    except:
        return []

def install_tesseract():
    """ติดตั้ง Tesseract OCR"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("กำลังติดตั้ง Tesseract OCR สำหรับ macOS...")
        subprocess.run(['brew', 'install', 'tesseract'])
    elif system == "Linux":
        print("กำลังติดตั้ง Tesseract OCR สำหรับ Linux...")
        subprocess.run(['sudo', 'apt-get', 'update'])
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'tesseract-ocr'])
    elif system == "Windows":
        print("สำหรับ Windows กรุณาติดตั้ง Tesseract OCR ด้วยตนเอง:")
        print("1. ดาวน์โหลดจาก: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. ติดตั้งและเพิ่ม path ไปยัง environment variables")
        return False
    else:
        print(f"ไม่รองรับระบบปฏิบัติการ: {system}")
        return False
    
    return check_tesseract_install()

def install_thai_language():
    """ติดตั้งข้อมูลภาษาไทยสำหรับ Tesseract"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        print("กำลังติดตั้งข้อมูลภาษาไทยสำหรับ macOS...")
        subprocess.run(['brew', 'install', 'tesseract-lang'])
    elif system == "Linux":
        print("กำลังติดตั้งข้อมูลภาษาไทยสำหรับ Linux...")
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'tesseract-ocr-tha'])
    elif system == "Windows":
        print("สำหรับ Windows กรุณาติดตั้งภาษาไทยผ่าน installer หรือดาวน์โหลดไฟล์ภาษาไทยด้วยตนเอง")
        return False
    else:
        print(f"ไม่รองรับระบบปฏิบัติการ: {system}")
        return False
    
    # ตรวจสอบว่าติดตั้งภาษาไทยสำเร็จหรือไม่
    langs = check_tesseract_languages()
    if 'tha' in langs:
        print("✅ ติดตั้งภาษาไทยสำหรับ Tesseract สำเร็จ")
        return True
    else:
        print("❌ ไม่สามารถตรวจพบภาษาไทยหลังการติดตั้ง")
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
    packages = ['pytesseract', 'pdf2image', 'pillow']
    
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
    
    # ตรวจสอบ Tesseract
    tesseract_installed = check_tesseract_install()
    if not tesseract_installed:
        print("❌ ไม่พบ Tesseract OCR")
    
    # ตรวจสอบภาษาไทย
    if tesseract_installed:
        langs = check_tesseract_languages()
        if 'tha' in langs:
            print("✅ พบข้อมูลภาษาไทยสำหรับ Tesseract")
        else:
            print("❌ ไม่พบข้อมูลภาษาไทยสำหรับ Tesseract")
    
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
    packages = ['tika', 'pytesseract', 'pdf2image', 'pillow']
    
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
        # ติดตั้ง Tesseract
        if not check_tesseract_install():
            install_tesseract()
        
        # ติดตั้งภาษาไทย
        langs = check_tesseract_languages()
        if 'tha' not in langs:
            install_thai_language()
        
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