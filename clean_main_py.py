#!/usr/bin/env python3
"""
Clean up main.py file to remove duplicate route definitions
"""

def clean_main_py():
    """Remove duplicate sections from main.py"""
    
    # Read the current file
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find where the generate_account_number function ends
    # This is where we want to truncate and add clean health checks
    truncate_marker = "        if not existing.data:\n            return account_number"
    
    if truncate_marker in content:
        # Find the position to truncate
        truncate_pos = content.find(truncate_marker) + len(truncate_marker)
        
        # Get the clean content up to this point
        clean_content = content[:truncate_pos]
        
        # Add the essential health check endpoints (no duplicates)
        health_checks = '''

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
        
        # Combine clean content with health checks
        final_content = clean_content + health_checks
        
        # Write the cleaned file
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print("✅ main.py cleaned successfully!")
        print("✅ Duplicate route definitions removed")
        print("✅ Essential health check endpoints added")
        
        return True
    else:
        print("❌ Could not find truncation marker in main.py")
        return False

if __name__ == "__main__":
    clean_main_py()
