"""
🔒 SOFI AI SECURITY AUDIT: INLINE KEYBOARD & PIN PROTECTION
===========================================================

Comprehensive security audit and fix for all Sofi responses to ensure:
1. No inline keyboards expose sensitive transaction URLs
2. PIN entry is secure and links are hidden
3. All password/security-related actions use secure methods

Created for Sofi AI Security Enhancement
"""

import os
import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class SofiSecurityAuditor:
    """Audit and fix security issues in Sofi AI responses"""
    
    def __init__(self):
        self.security_violations = []
        self.fixed_responses = []
        
    def audit_response_security(self, response_data: Dict) -> Dict:
        """Audit a response for security violations"""
        violations = []
        
        # Check if this is a legitimate Sofi PIN entry flow
        is_legitimate_pin_flow = (
            response_data.get('feature_version') == 'v2.1_inline_keyboard' and
            response_data.get('keyboard_type') == 'inline_web_app' and
            response_data.get('requires_pin') == True
        )
        
        # Check for inline keyboards with sensitive URLs (but allow legitimate PIN entry)
        if 'keyboard' in response_data or 'reply_markup' in response_data:
            keyboard_data = response_data.get('keyboard') or response_data.get('reply_markup')
            if keyboard_data and 'inline_keyboard' in keyboard_data:
                if not is_legitimate_pin_flow:
                    violations.extend(self._check_inline_keyboard_security(keyboard_data['inline_keyboard']))
                # If it's legitimate PIN flow, we still check but are more lenient
                elif is_legitimate_pin_flow:
                    # For legitimate PIN flows, only check for truly malicious patterns
                    violations.extend(self._check_legitimate_pin_keyboard(keyboard_data['inline_keyboard']))
        
        # Check for exposed PIN/password URLs in message text
        message = response_data.get('message', '')
        if message:
            violations.extend(self._check_message_security(message))
        
        # Check for transaction IDs or sensitive data in URLs (but allow legitimate PIN flows)
        if not is_legitimate_pin_flow and ('pin_url' in response_data or 'verification_url' in response_data):
            violations.append({
                'type': 'exposed_url',
                'severity': 'HIGH',
                'description': 'Sensitive URL exposed in response data',
                'recommendation': 'Use secure PIN entry without exposing URLs'
            })
        
        return {
            'secure': len(violations) == 0,
            'violations': violations,
            'security_score': max(0, 100 - (len(violations) * 20))
        }
    
    def _check_inline_keyboard_security(self, inline_keyboard: List) -> List[Dict]:
        """Check inline keyboard for security issues"""
        violations = []
        
        for row in inline_keyboard:
            for button in row:
                # Check for web_app buttons with sensitive URLs
                if 'web_app' in button:
                    url = button['web_app'].get('url', '')
                    if self._is_sensitive_url(url):
                        violations.append({
                            'type': 'sensitive_web_app_url',
                            'severity': 'CRITICAL',
                            'description': f'Sensitive URL in web_app button: {url}',
                            'recommendation': 'Remove web_app buttons for PIN entry, use voice/text instead'
                        })
                
                # Check for callback_data with sensitive information
                if 'callback_data' in button:
                    callback_data = button['callback_data']
                    if self._contains_sensitive_data(callback_data):
                        violations.append({
                            'type': 'sensitive_callback_data',
                            'severity': 'HIGH',
                            'description': f'Sensitive data in callback: {callback_data}',
                            'recommendation': 'Use secure session storage instead of exposing data in callbacks'
                        })
        
        return violations
    
    def _check_legitimate_pin_keyboard(self, inline_keyboard: List) -> List[Dict]:
        """Check legitimate PIN entry keyboards for only serious security issues"""
        violations = []
        
        for row in inline_keyboard:
            for button in row:
                # For legitimate PIN flows, only flag truly malicious patterns
                if 'web_app' in button:
                    url = button['web_app'].get('url', '')
                    
                    # Only flag if it's not our official domain
                    if url and 'pipinstallsofi.com' not in url:
                        violations.append({
                            'type': 'external_web_app_url',
                            'severity': 'CRITICAL',
                            'description': f'External web app URL detected: {url}',
                            'recommendation': 'Use only official pipinstallsofi.com domain for PIN entry'
                        })
                    
                    # Flag if PIN is embedded in URL (very insecure)
                    if re.search(r'pin=\d+|password=', url, re.IGNORECASE):
                        violations.append({
                            'type': 'pin_in_url',
                            'severity': 'CRITICAL', 
                            'description': 'PIN or password embedded in URL',
                            'recommendation': 'Never embed PIN in URLs'
                        })
        
        return violations

    def _check_message_security(self, message: str) -> List[Dict]:
        """Check message content for security issues"""
        violations = []
        
        # Only flag URLs that are actually insecure (not our legitimate web app)
        insecure_url_pattern = r'https?://(?!sofi-ai-deploy\.onrender\.com)[^\s]+(?:pin|password)[^\s]*'
        if re.search(insecure_url_pattern, message, re.IGNORECASE):
            violations.append({
                'type': 'exposed_transaction_url',
                'severity': 'HIGH',
                'description': 'Insecure external URL exposed in message text',
                'recommendation': 'Use secure web app PIN entry instead'
            })
        
        # Check for truly insecure PIN instructions (direct links, not web app buttons)
        insecure_patterns = [
            r'click.*this.*link.*pin',  # Direct link clicking for PIN
            r'visit.*http.*pin',        # Direct URL visits for PIN
            r'go.*to.*url.*pin'         # Direct navigation for PIN
        ]
        
        for pattern in insecure_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                violations.append({
                    'type': 'insecure_pin_instruction',
                    'severity': 'MEDIUM',
                    'description': f'Potentially insecure PIN instruction found',
                    'recommendation': 'Use voice or secure text PIN entry only'
                })
        
        return violations
    
    def _is_sensitive_url(self, url: str) -> bool:
        """Check if URL contains sensitive information that's actually insecure"""
        # Allow legitimate web app PIN entry URLs from our own domain
        if 'sofi-ai-deploy.onrender.com/enter-pin' in url:
            return False  # This is a legitimate secure PIN entry web app
        
        # Flag URLs that expose sensitive info in insecure ways
        insecure_patterns = [
            r'pin=\d+',  # PIN in URL parameters (insecure)
            r'password=',  # Password in URL (insecure)  
            r'verify-pin.*example\.com',  # Demo/test URLs (insecure)
            r'auth.*token=',  # Auth tokens in URL (insecure)
        ]
        
        return any(re.search(pattern, url, re.IGNORECASE) for pattern in insecure_patterns)
    
    def _contains_sensitive_data(self, data: str) -> bool:
        """Check if callback data contains sensitive information"""
        sensitive_indicators = [
            'transaction_',
            'txn_',
            'pin_',
            'password_',
            'verify_transfer_',
            '_amount_',
            '_account_'
        ]
        
        return any(indicator in data.lower() for indicator in sensitive_indicators)
    
    def create_secure_response(self, original_response: Dict) -> Dict:
        """Create a secure version of a response"""
        secure_response = original_response.copy()
        
        # Remove any inline keyboards for PIN/password operations
        if 'keyboard' in secure_response:
            del secure_response['keyboard']
        if 'reply_markup' in secure_response:
            del secure_response['reply_markup']
        
        # Remove exposed URLs
        sensitive_keys = ['pin_url', 'verification_url', 'auth_url']
        for key in sensitive_keys:
            if key in secure_response:
                del secure_response[key]
        
        # Update message to be security-focused
        if 'message' in secure_response and 'pin' in secure_response['message'].lower():
            secure_response['message'] = self._create_secure_pin_message(secure_response['message'])
        
        # Add security metadata
        secure_response['security_enhanced'] = True
        secure_response['security_note'] = "Links hidden for security"
        
        return secure_response
    
    def _create_secure_pin_message(self, original_message: str) -> str:
        """Create a secure PIN entry message"""
        return """🔐 **SECURE PIN ENTRY REQUIRED**

For your security and privacy:
• Send your 4-digit PIN as voice message (speak clearly: "1 2 3 4")
• Or type: PIN 1234
• PIN entry links are hidden to protect your transaction

⚠️ **SECURITY FEATURES:**
• Your PIN is encrypted and never stored
• Transaction links are not exposed in messages
• All transfers require secure PIN verification
• Session expires automatically for safety

Continue with voice or text PIN to proceed securely."""

# Global security auditor instance
security_auditor = SofiSecurityAuditor()

def audit_sofi_response(response: Dict) -> Dict:
    """Audit any Sofi response for security issues"""
    return security_auditor.audit_response_security(response)

def secure_sofi_response(response: Dict) -> Dict:
    """Make any Sofi response secure"""
    audit_result = audit_sofi_response(response)
    
    if not audit_result['secure']:
        logger.warning(f"🚨 Security violations found: {len(audit_result['violations'])}")
        for violation in audit_result['violations']:
            logger.warning(f"   {violation['severity']}: {violation['description']}")
        
        # Create secure version
        secure_response = security_auditor.create_secure_response(response)
        logger.info("✅ Response secured - sensitive elements removed")
        return secure_response
    
    return response

def validate_transfer_response(transfer_result: Dict) -> Dict:
    """Specifically validate transfer responses for security"""
    if transfer_result.get('requires_pin'):
        # Ensure no inline keyboards for PIN entry
        if 'keyboard' in transfer_result or 'pin_url' in transfer_result:
            logger.warning("🚨 Removing insecure PIN entry method")
            return security_auditor.create_secure_response(transfer_result)
    
    return transfer_result

# Export for easy import
__all__ = [
    'security_auditor',
    'audit_sofi_response', 
    'secure_sofi_response',
    'validate_transfer_response'
]
