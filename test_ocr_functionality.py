#!/usr/bin/env python3
"""
Test script for OCR image processing functionality
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from PIL import Image, ImageDraw, ImageFont
import io
from utils.media_processor import MediaProcessor

def create_test_image_with_account():
    """Create a test image with account details"""
    # Create a simple image with account details
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    # Add some account details to the image
    text_lines = [
        "ACCESS BANK",
        "Account Number: 1234567890", 
        "Account Name: John Doe",
        "Available Balance: N5,000.00"
    ]
    
    y_position = 50
    for line in text_lines:
        draw.text((20, y_position), line, fill='black', font=font)
        y_position += 40
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def test_ocr_functionality():
    """Test the OCR functionality"""
    print("Testing OCR functionality...")
    
    # Create test image with account details
    test_image_bytes = create_test_image_with_account()
    print(f"Created test image: {len(test_image_bytes)} bytes")
    
    # Test the MediaProcessor
    try:
        result = MediaProcessor.process_image(test_image_bytes)
        print(f"OCR Result: {result}")
        
        if result:
            print("✅ OCR successfully extracted data:")
            if result.get("account_number"):
                print(f"  📱 Account Number: {result['account_number']}")
            if result.get("bank"):
                print(f"  🏦 Bank: {result['bank']}")
            if result.get("account_name"):
                print(f"  👤 Account Name: {result['account_name']}")
        else:
            print("❌ OCR did not extract any account details")
            
        return result is not None
        
    except Exception as e:
        print(f"❌ Error testing OCR: {e}")
        return False

if __name__ == "__main__":
    success = test_ocr_functionality()
    if success:
        print("\n🎉 OCR test completed successfully!")
    else:
        print("\n💥 OCR test failed!")
