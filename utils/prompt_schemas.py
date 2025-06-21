"""
🤖 STANDARDIZED PROMPT SCHEMAS FOR SOFI AI

This module contains standardized prompts and JSON schemas for:
1. Transfer information extraction
2. Image analysis for financial documents
3. Consistent error handling and field definitions

Fixes all prompt engineering issues identified in OpenAI logs.
"""

import json
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class TransferExtractionResult:
    """Standardized result for transfer information extraction"""
    amount: Optional[float] = None
    account: Optional[str] = None
    bank: Optional[str] = None
    recipient: Optional[str] = None
    error: Optional[str] = None

@dataclass 
class ImageAnalysisResult:
    """Standardized result for image analysis"""
    document_type: str  # "bank_details", "transaction", "other"
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    account_holder: Optional[str] = None
    amount: Optional[float] = None
    error: Optional[str] = None

class PromptSchemas:
    """Centralized prompt schemas with consistent JSON output formats"""
    
    @staticmethod
    def get_transfer_extraction_prompt() -> str:
        """
        Get standardized prompt for extracting transfer information from text messages.
        Returns consistent JSON schema regardless of input format.
        """
        return """You are a Nigerian banking assistant that extracts transfer information from messages.

TASK: Extract transfer details and return standardized JSON.

OUTPUT SCHEMA (always include all fields):
{
    "amount": number or null,        // Convert k/thousand to actual number, remove currency symbols
    "account": string or null,       // 10-11 digit account number only
    "bank": string or null,          // Full bank name (e.g., "Access Bank", "GTBank", "Opay")
    "recipient": string or null,     // Recipient name if mentioned
    "error": string or null          // Error message if extraction impossible
}

EXTRACTION RULES:
1. Amount: Convert "5k" → 5000, "₦2000" → 2000, "2.5k" → 2500
2. Account: Must be 10-11 digits, ignore invalid numbers
3. Bank: Recognize Nigerian banks (Access, GTB, Zenith, UBA, First Bank, Opay, Palmpay, etc.)
4. Recipient: Any name mentioned as receiver
5. Error: Set if no transfer intent detected or critical info missing

EXAMPLES:
Input: "Send 5k to 1234567891 access bank"
Output: {"amount": 5000, "account": "1234567891", "bank": "Access Bank", "recipient": null, "error": null}

Input: "Transfer ₦2000 to 0123456789"
Output: {"amount": 2000, "account": "0123456789", "bank": null, "recipient": null, "error": null}

Input: "8104611794 Opay mella"
Output: {"amount": null, "account": "8104611794", "bank": "Opay", "recipient": "mella", "error": null}

Input: "Hey SoFi"
Output: {"amount": null, "account": null, "bank": null, "recipient": null, "error": "No transfer information found in message"}

Input: "Sophie, I want to send airtime to somebody"
Output: {"amount": null, "account": null, "bank": null, "recipient": null, "error": "Airtime request detected, not a bank transfer"}

IMPORTANT: Always return valid JSON with all 5 fields present."""

    @staticmethod
    def get_image_analysis_prompt() -> str:
        """
        Get standardized prompt for analyzing financial document images.
        Returns consistent JSON schema for all document types.
        """
        return """You are analyzing images for Sofi AI, a Nigerian fintech bot.

TASK: Analyze financial document images and extract key information.

OUTPUT SCHEMA (always include all fields):
{
    "type": string,                  // "bank_details", "transaction", or "other"
    "details": {
        "account_number": string or null,    // 10-digit bank account number
        "bank_name": string or null,         // Full bank name
        "account_holder": string or null,    // Account owner's name
        "amount": number or null             // Most prominent monetary amount
    },
    "error": string or null          // Error if analysis fails
}

ANALYSIS RULES:
1. Type Classification:
   - "bank_details": Bank account screenshots, account statements, bank card images
   - "transaction": Transaction receipts, payment confirmations, transfer slips
   - "other": Any financial document that doesn't fit above categories

2. Field Extraction:
   - account_number: Extract 10-digit Nigerian bank account numbers only
   - bank_name: Full bank names (GTBank, Access Bank, Zenith Bank, etc.)
   - account_holder: Name of account owner or recipient
   - amount: Most prominent monetary figure (convert to number, no currency symbols)

3. Error Handling:
   - Set error if image is unreadable, corrupted, or not financial document
   - Set fields to null if specific information cannot be extracted
   - Still provide partial information even if some fields are missing

EXAMPLES:
Bank Account Screenshot:
{
    "type": "bank_details",
    "details": {
        "account_number": "0123456789",
        "bank_name": "GTBank",
        "account_holder": "John Doe",
        "amount": 150000.00
    },
    "error": null
}

Transaction Receipt:
{
    "type": "transaction", 
    "details": {
        "account_number": null,
        "bank_name": "Zenith Bank",
        "account_holder": null,
        "amount": 12000.00
    },
    "error": null
}

Unreadable Image:
{
    "type": "other",
    "details": {
        "account_number": null,
        "bank_name": null, 
        "account_holder": null,
        "amount": null
    },
    "error": "Image quality too poor to extract information"
}

IMPORTANT: Always return valid JSON with complete schema structure."""

    @staticmethod
    def validate_transfer_extraction(result: Dict[str, Any]) -> TransferExtractionResult:
        """
        Validate and standardize transfer extraction result
        
        Args:
            result: Raw result from AI extraction
            
        Returns:
            TransferExtractionResult: Validated and standardized result
        """
        try:
            # Ensure all required fields exist
            amount = result.get("amount")
            account = result.get("account") 
            bank = result.get("bank")
            recipient = result.get("recipient")
            error = result.get("error")
            
            # Validate amount
            if amount is not None:
                try:
                    amount = float(amount)
                    if amount <= 0:
                        amount = None
                except (ValueError, TypeError):
                    amount = None
            
            # Validate account number
            if account is not None:
                account = str(account).strip()
                if not account.isdigit() or len(account) not in [10, 11]:
                    account = None
            
            # Validate bank name
            if bank is not None:
                bank = str(bank).strip()
                if len(bank) < 2:
                    bank = None
            
            # Validate recipient
            if recipient is not None:
                recipient = str(recipient).strip()
                if len(recipient) < 2:
                    recipient = None
            
            return TransferExtractionResult(
                amount=amount,
                account=account, 
                bank=bank,
                recipient=recipient,
                error=error
            )
            
        except Exception as e:
            return TransferExtractionResult(
                error=f"Validation error: {str(e)}"
            )
    
    @staticmethod
    def validate_image_analysis(result: Dict[str, Any]) -> ImageAnalysisResult:
        """
        Validate and standardize image analysis result
        
        Args:
            result: Raw result from AI analysis
            
        Returns:
            ImageAnalysisResult: Validated and standardized result
        """
        try:
            document_type = result.get("type", "other")
            if document_type not in ["bank_details", "transaction", "other"]:
                document_type = "other"
            
            details = result.get("details", {})
            error = result.get("error")
            
            # Validate account number
            account_number = details.get("account_number")
            if account_number is not None:
                account_number = str(account_number).strip()
                if not account_number.isdigit() or len(account_number) != 10:
                    account_number = None
            
            # Validate bank name
            bank_name = details.get("bank_name")
            if bank_name is not None:
                bank_name = str(bank_name).strip()
                if len(bank_name) < 2:
                    bank_name = None
            
            # Validate account holder
            account_holder = details.get("account_holder")
            if account_holder is not None:
                account_holder = str(account_holder).strip()
                if len(account_holder) < 2:
                    account_holder = None
            
            # Validate amount
            amount = details.get("amount")
            if amount is not None:
                try:
                    amount = float(amount)
                    if amount <= 0:
                        amount = None
                except (ValueError, TypeError):
                    amount = None
            
            return ImageAnalysisResult(
                document_type=document_type,
                account_number=account_number,
                bank_name=bank_name,
                account_holder=account_holder,
                amount=amount,
                error=error
            )
            
        except Exception as e:
            return ImageAnalysisResult(
                document_type="other",
                error=f"Validation error: {str(e)}"
            )

    @staticmethod
    def get_nigerian_banks_list() -> list:
        """Get list of recognized Nigerian banks for prompt context"""
        return [
            "Access Bank", "GTBank", "Zenith Bank", "UBA", "First Bank", 
            "Fidelity Bank", "FCMB", "Unity Bank", "Sterling Bank", "Wema Bank",
            "Polaris Bank", "Keystone Bank", "Stanbic IBTC", "Citibank Nigeria",
            "Heritage Bank", "Providus Bank", "SunTrust Bank", "Titan Trust Bank",
            "Opay", "Palmpay", "Kuda Bank", "Carbon", "Fairmoney", "Renmoney",
            "ALAT by Wema", "V Bank", "Rubies Bank", "Moniepoint", "VFD Bank",
            "Globus Bank", "PremiumTrust Bank", "TAJ Bank", "Parallex Bank"
        ]
    
    @staticmethod
    def format_json_response(data: Dict[str, Any]) -> str:
        """
        Format response as clean JSON string
        
        Args:
            data: Dictionary to format
            
        Returns:
            str: Clean JSON string
        """
        try:
            return json.dumps(data, indent=None, separators=(',', ':'), ensure_ascii=False)
        except Exception:
            # Fallback for problematic data
            return json.dumps({"error": "Failed to format response"})

# Global instances for easy access
prompt_schemas = PromptSchemas()

# Export key functions
def get_transfer_prompt() -> str:
    """Get standardized transfer extraction prompt"""
    return prompt_schemas.get_transfer_extraction_prompt()

def get_image_prompt() -> str:
    """Get standardized image analysis prompt"""
    return prompt_schemas.get_image_analysis_prompt()

def validate_transfer_result(result: Dict[str, Any]) -> TransferExtractionResult:
    """Validate transfer extraction result"""
    return prompt_schemas.validate_transfer_extraction(result)

def validate_image_result(result: Dict[str, Any]) -> ImageAnalysisResult:
    """Validate image analysis result"""
    return prompt_schemas.validate_image_analysis(result)
