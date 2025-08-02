#!/usr/bin/env python3
"""
Remove duplicated sections from main.py completely
"""

def remove_all_duplicates():
    """Remove all duplicated content from main.py"""
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Original file size: {len(content)} characters")
        
        # Find the last occurrence of generate_account_number function ending
        marker = "        if not existing.data:\n            return account_number"
        
        if marker in content:
            # Find ALL occurrences of this marker
            marker_positions = []
            start = 0
            while True:
                pos = content.find(marker, start)
                if pos == -1:
                    break
                marker_positions.append(pos + len(marker))
                start = pos + 1
            
            print(f"Found marker at positions: {marker_positions}")
            
            if marker_positions:
                # Use the FIRST occurrence (the real one, not duplicated)
                truncate_pos = marker_positions[0]
                clean_content = content[:truncate_pos]
                
                print(f"Truncating at position: {truncate_pos}")
                print(f"Clean content size: {len(clean_content)} characters")
                
                # Add the health check endpoints ONCE
                health_section = '''

# ===============================================
# 🏥 HEALTH CHECK ENDPOINTS  
# ===============================================

@app.route("/health")
def health_check():
    """Health check endpoint for Meta Business Manager"""
    return jsonify({
        "status": "healthy",
        "service": "Sofi WhatsApp Flow",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "whatsapp_webhook": "/whatsapp-webhook",
            "flow_webhook": "/whatsapp-flow-webhook"
        }
    }), 200

@app.route("/health/flow", methods=["GET"])
def flow_health_check():
    """Flow-specific health check endpoint with encryption status"""
    try:
        # Test encryption setup
        flow_encryption = get_flow_encryption()
        encryption_status = "ready" if flow_encryption else "not available"
        
        return jsonify({
            "status": "healthy",
            "service": "Sofi WhatsApp Flow Endpoint", 
            "timestamp": datetime.utcnow().isoformat(),
            "encryption": encryption_status,
            "endpoints": {
                "flow_webhook": "/whatsapp-flow-webhook",
                "health": "/health",
                "flow_health": "/health/flow"
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@app.route("/whatsapp-flow-webhook/health")
def flow_webhook_health():
    """Specific health check for Flow webhook"""
    return jsonify({
        "status": "ready",
        "webhook": "whatsapp-flow",
        "accepts": ["GET", "POST"],
        "verification": "enabled"
    }), 200

# ===============================================
# 🚀 APPLICATION STARTUP
# ===============================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
'''
                
                # Create the final clean file
                final_content = clean_content + health_section
                
                print(f"Final content size: {len(final_content)} characters")
                
                # Write the cleaned file
                with open('main.py', 'w', encoding='utf-8') as f:
                    f.write(final_content)
                
                print("✅ File cleaned and deduplicated!")
                
                # Verify the fix
                with open('main.py', 'r', encoding='utf-8') as f:
                    new_content = f.read()
                
                health_count = new_content.count('@app.route("/health")')
                flow_count = new_content.count('@app.route("/health/flow")')
                webhook_count = new_content.count('@app.route("/whatsapp-flow-webhook/health")')
                
                print(f"\nVerification:")
                print(f"  /health routes: {health_count}")
                print(f"  /health/flow routes: {flow_count}")
                print(f"  /whatsapp-flow-webhook/health routes: {webhook_count}")
                print(f"  Total file size: {len(new_content)} characters")
                
                if health_count == 1 and flow_count == 1 and webhook_count == 1:
                    print("✅ All routes are now unique!")
                    return True
                else:
                    print("❌ Still have duplicate routes")
                    return False
            else:
                print("❌ No marker positions found")
                return False
        else:
            print("❌ Could not find truncation marker")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    remove_all_duplicates()
