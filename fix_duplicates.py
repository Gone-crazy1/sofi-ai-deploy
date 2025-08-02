#!/usr/bin/env python3
"""
Check for duplicate routes in main.py and fix them
"""

def check_and_fix_duplicates():
    """Check for duplicate route definitions and fix them"""
    
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count occurrences of route definitions
        health_route_count = content.count('@app.route("/health")')
        health_flow_count = content.count('@app.route("/health/flow")')
        webhook_health_count = content.count('@app.route("/whatsapp-flow-webhook/health")')
        
        print(f"Route occurrence count:")
        print(f"  /health: {health_route_count}")
        print(f"  /health/flow: {health_flow_count}")
        print(f"  /whatsapp-flow-webhook/health: {webhook_health_count}")
        
        if health_route_count > 1 or health_flow_count > 1 or webhook_health_count > 1:
            print("\n❌ Duplicate routes found! Fixing...")
            
            # Find the last occurrence of generate_account_number function
            marker = "        if not existing.data:\n            return account_number"
            
            if marker in content:
                # Truncate at the end of generate_account_number
                truncate_pos = content.find(marker) + len(marker)
                clean_content = content[:truncate_pos]
                
                # Add clean health check endpoints
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
                
                # Write the cleaned file
                with open('main.py', 'w', encoding='utf-8') as f:
                    f.write(final_content)
                
                print("✅ Duplicates removed successfully!")
                print("✅ Clean health check endpoints added")
                
                # Verify the fix
                with open('main.py', 'r', encoding='utf-8') as f:
                    new_content = f.read()
                
                new_health_count = new_content.count('@app.route("/health")')
                new_flow_count = new_content.count('@app.route("/health/flow")')
                new_webhook_count = new_content.count('@app.route("/whatsapp-flow-webhook/health")')
                
                print(f"\nAfter fix:")
                print(f"  /health: {new_health_count}")
                print(f"  /health/flow: {new_flow_count}")
                print(f"  /whatsapp-flow-webhook/health: {new_webhook_count}")
                
                return True
            else:
                print("❌ Could not find truncation point")
                return False
        else:
            print("✅ No duplicate routes found!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    check_and_fix_duplicates()
