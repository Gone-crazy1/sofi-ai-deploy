#!/usr/bin/env python3
"""
Test the improved image processing functionality without OCR dependency
"""
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from PIL import Image, ImageDraw, ImageFont
import io
from unittest.mock import patch, MagicMock

def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # Add some text to the image
    text_lines = [
        "ACCESS BANK",
        "Account: 1234567890", 
        "Name: John Doe"
    ]
    
    y_position = 50
    for line in text_lines:
        draw.text((20, y_position), line, fill='black', font=font)
        y_position += 40
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()

def test_image_processing_fallback():
    """Test image processing fallback functionality"""
    print("Testing image processing fallback...")
    
    # Mock the required functions
    with patch('main.download_file') as mock_download, \
         patch('main.openai.ChatCompletion.create') as mock_openai, \
         patch('main.logger') as mock_logger:
        
        # Setup mocks
        test_image_data = create_test_image()
        mock_download.return_value = test_image_data
        
        mock_openai.return_value = {
            'choices': [{
                'message': {
                    'content': 'I can see this appears to be a bank account screenshot with Access Bank details. Would you like me to help you transfer money to this account?'
                }
            }]
        }
        
        # Import and test the function
        from main import process_photo
        
        try:
            success, response = process_photo("test_file_id")
            
            print(f"Success: {success}")
            print(f"Response: {response}")
            
            # Verify the response contains helpful banking content
            assert success == True
            assert "bank" in response.lower() or "account" in response.lower()
            
            print("✅ Image processing fallback test passed!")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

if __name__ == "__main__":
    success = test_image_processing_fallback()
    if success:
        print("\n🎉 Image processing test completed successfully!")
    else:
        print("\n💥 Image processing test failed!")
