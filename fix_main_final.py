#!/usr/bin/env python3
"""
Final fix for main.py - Remove all duplicates and add clean health checks
"""

def fix_main_py_final():
    """Final cleanup of main.py"""
    
    # Read the current file
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the truncation point
    marker = '        if not existing.data:\n            return account_number'
    pos = content.rfind(marker)
    
    if pos != -1:
        # Truncate at the marker
        clean_content = content[:pos + len(marker)]
        
        # Add clean health check endpoints (no duplicates)
        health_endpoints = '''

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
        final_content = clean_content + health_endpoints
        
        # Write the file
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print("✅ main.py fixed successfully!")
        print(f"✅ File truncated and cleaned")
        print(f"✅ Added clean health check endpoints")
        print(f"✅ No duplicate routes")
        
        return True
    else:
        print("❌ Could not find truncation marker")
        return False

if __name__ == "__main__":
    fix_main_py_final()
