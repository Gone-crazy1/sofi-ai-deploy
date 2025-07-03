"""
Preview the HTML receipt design
"""

import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.receipt_generator import SofiReceiptGenerator

def preview_receipt():
    """Generate HTML receipt for preview"""
    
    # Sample transaction data
    receipt_data = {
        'amount': 50000,
        'fee': 100,
        'total_charged': 50100,
        'new_balance': 75000,
        'recipient_name': 'JOHN MICHAEL SMITH',
        'bank_name': 'First Bank Nigeria (FBN)',
        'account_number': '8104965538',
        'reference': 'TRF_kd5hj6pwjasba52l',
        'transaction_id': 'TXN_67890',
        'transaction_time': '03/07/2025 02:30 PM',
        'narration': 'Transfer to John Michael Smith'
    }
    
    print("🎨 Generating HTML receipt preview...")
    
    # Generate receipt
    generator = SofiReceiptGenerator()
    html_content = generator.generate_html_receipt(receipt_data)
    
    if html_content:
        # Save to file
        with open("receipt_preview.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print("✅ HTML receipt saved as 'receipt_preview.html'")
        print("🌐 Open this file in your browser to preview the design")
        print("📱 This is how the receipt will look when converted to image")
        
        return True
    else:
        print("❌ Failed to generate HTML receipt")
        return False

if __name__ == "__main__":
    preview_receipt()
