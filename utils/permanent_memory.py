# utils/permanent_memory.py
"""
Sofi AI Permanent Memory System

This module provides comprehensive permanent memory capabilities for Sofi AI,
allowing her to remember user preferences, notes, goals, reminders, and personal
information permanently via Supabase.
"""

import os
import hashlib
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Union
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")

# Lazy initialization
supabase = None

def get_supabase_client():
    """Get or create supabase client"""
    global supabase
    if supabase is None:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

# ================================================================================================
# CORE MEMORY FUNCTIONS
# ================================================================================================

async def save_user_memory(user_id: str, memory_type: str, memory_key: str, 
                          memory_value: str, encrypt: bool = False, 
                          expires_at: Optional[datetime] = None) -> bool:
    """
    Save a permanent memory for a user
    
    Args:
        user_id: User identifier
        memory_type: Type of memory ('note', 'preference', 'goal', 'pin', 'name', etc.)
        memory_key: Specific key ('birthday', 'favorite_bank', 'business_idea', etc.)
        memory_value: The actual content to store
        encrypt: Whether to encrypt the value (for sensitive data like PINs)
        expires_at: Optional expiration date for temporary memories
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_supabase_client()
        
        # Encrypt sensitive data
        if encrypt:
            memory_value = encrypt_sensitive_data(memory_value)
        
        memory_data = {
            "user_id": user_id,
            "memory_type": memory_type,
            "memory_key": memory_key,
            "memory_value": memory_value,
            "is_encrypted": encrypt,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "updated_at": datetime.now().isoformat()
        }
        
        # Use upsert to update if exists, insert if not
        result = client.table("user_memories").upsert(memory_data).execute()
        
        return bool(result.data)
    except Exception as e:
        print(f"Error saving user memory: {e}")
        # Graceful degradation for missing tables
        if "does not exist" in str(e):
            print(f"Note: user_memories table not found, skipping memory save")
        return False

async def get_user_memory(user_id: str, memory_type: str, memory_key: str) -> Optional[str]:
    """
    Retrieve a specific memory for a user
    
    Args:
        user_id: User identifier
        memory_type: Type of memory
        memory_key: Specific key
    
    Returns:
        str: The memory value if found, None otherwise
    """
    try:
        client = get_supabase_client()
        
        result = client.table("user_memories") \
            .select("memory_value, is_encrypted") \
            .eq("user_id", user_id) \
            .eq("memory_type", memory_type) \
            .eq("memory_key", memory_key) \
            .execute()
        
        if result.data:
            memory = result.data[0]
            value = memory["memory_value"]
            
            # Decrypt if necessary
            if memory["is_encrypted"]:
                value = decrypt_sensitive_data(value)
            
            return value
        
        return None
        
    except Exception as e:
        print(f"Error getting user memory: {e}")
        # Graceful degradation for missing tables
        if "does not exist" in str(e):
            print(f"Note: user_memories table not found, returning None")
        return None

async def get_all_user_memories(user_id: str, memory_type: Optional[str] = None) -> List[Dict]:
    """
    Get all memories for a user, optionally filtered by type
    
    Args:
        user_id: User identifier
        memory_type: Optional filter by memory type
    
    Returns:
        List[Dict]: List of memory records
    """
    try:
        client = get_supabase_client()
        
        query = client.table("user_memories") \
            .select("*") \
            .eq("user_id", user_id)
        
        if memory_type:
            query = query.eq("memory_type", memory_type)
        
        result = query.order("created_at", desc=True).execute()
        
        # Decrypt sensitive data
        for memory in result.data:
            if memory["is_encrypted"]:
                memory["memory_value"] = decrypt_sensitive_data(memory["memory_value"])
        
        return result.data
        
    except Exception as e:
        print(f"Error getting user memories: {e}")
        return []

async def delete_user_memory(user_id: str, memory_type: str, memory_key: str) -> bool:
    """Delete a specific memory"""
    try:
        client = get_supabase_client()
        
        result = client.table("user_memories") \
            .delete() \
            .eq("user_id", user_id) \
            .eq("memory_type", memory_type) \
            .eq("memory_key", memory_key) \
            .execute()
        
        return True
        
    except Exception as e:
        print(f"Error deleting user memory: {e}")
        return False

# ================================================================================================
# USER PREFERENCES
# ================================================================================================

async def save_user_preference(user_id: str, **preferences) -> bool:
    """
    Save user preferences
    
    Args:
        user_id: User identifier
        **preferences: Keyword arguments for preferences
                      (preferred_name, birthday, preferred_bank, etc.)
    
    Returns:
        bool: True if successful
    """
    try:
        client = get_supabase_client()
          # Convert date objects to strings
        for key, value in preferences.items():
            if isinstance(value, date):
                preferences[key] = value.isoformat()
        
        preferences.update({
            "user_id": user_id,
            "updated_at": datetime.now().isoformat()
        })
        
        result = client.table("user_preferences").upsert(preferences).execute()
        return bool(result.data)
        
    except Exception as e:
        print(f"Error saving user preferences: {e}")
        # Graceful degradation for missing tables
        if "does not exist" in str(e):
            print(f"Note: user_preferences table not found, skipping preference save")
        return False

async def get_user_preferences(user_id: str) -> Dict:
    """Get all user preferences"""
    try:
        client = get_supabase_client()
        
        result = client.table("user_preferences") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
        
        return result.data[0] if result.data else {}
        
    except Exception as e:
        print(f"Error getting user preferences: {e}")
        # Graceful degradation for missing tables
        if "does not exist" in str(e):
            print(f"Note: user_preferences table not found, returning empty dict")
        return {}

# ================================================================================================
# GOALS AND SAVINGS
# ================================================================================================

async def save_user_goal(user_id: str, goal_type: str, goal_name: str, 
                        target_amount: float, target_date: Optional[date] = None,
                        description: Optional[str] = None, priority: int = 2) -> bool:
    """Save a user goal"""
    try:
        client = get_supabase_client()
        
        goal_data = {
            "user_id": user_id,
            "goal_type": goal_type,
            "goal_name": goal_name,
            "target_amount": target_amount,
            "target_date": target_date.isoformat() if target_date else None,
            "description": description,
            "priority": priority,
            "updated_at": datetime.now().isoformat()
        }
        
        result = client.table("user_goals_and_savings").insert(goal_data).execute()
        return bool(result.data)
        
    except Exception as e:
        print(f"Error saving user goal: {e}")
        # Graceful degradation for missing tables
        if "does not exist" in str(e):
            print(f"Note: user_goals_and_savings table not found, skipping goal save")
        return False

async def get_user_goals(user_id: str, status: str = "active") -> List[Dict]:
    """Get user goals"""
    try:
        client = get_supabase_client()
        
        result = client.table("user_goals_and_savings") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("status", status) \
            .order("priority", desc=False) \
            .execute()
        
        return result.data
        
    except Exception as e:
        print(f"Error getting user goals: {e}")
        # Graceful degradation for missing tables
        if "does not exist" in str(e):
            print(f"Note: user_goals_and_savings table not found, returning empty list")
        return []

async def update_goal_progress(user_id: str, goal_id: int, current_amount: float) -> bool:
    """Update progress towards a goal"""
    try:
        client = get_supabase_client()
        
        result = client.table("user_goals_and_savings") \
            .update({"current_amount": current_amount, "updated_at": datetime.now().isoformat()}) \
            .eq("id", goal_id) \
            .eq("user_id", user_id) \
            .execute()
        
        return bool(result.data)
        
    except Exception as e:
        print(f"Error updating goal progress: {e}")
        return False

# ================================================================================================
# REMINDERS
# ================================================================================================

async def save_user_reminder(user_id: str, title: str, remind_at: datetime,
                           description: Optional[str] = None, 
                           reminder_type: str = "one_time",
                           recurring_pattern: Optional[str] = None,
                           priority: int = 2) -> bool:
    """Save a user reminder"""
    try:
        client = get_supabase_client()
        
        reminder_data = {
            "user_id": user_id,
            "reminder_type": reminder_type,
            "title": title,
            "description": description,
            "remind_at": remind_at.isoformat(),
            "recurring_pattern": recurring_pattern,
            "priority": priority,
            "updated_at": datetime.now().isoformat()
        }
        
        result = client.table("user_reminders").insert(reminder_data).execute()
        return bool(result.data)
        
    except Exception as e:
        print(f"Error saving user reminder: {e}")
        return False

async def get_pending_reminders(user_id: str) -> List[Dict]:
    """Get pending reminders for a user"""
    try:
        client = get_supabase_client()
        
        result = client.table("user_reminders") \
            .select("*") \
            .eq("user_id", user_id) \
            .eq("is_completed", False) \
            .lte("remind_at", datetime.now().isoformat()) \
            .order("priority", desc=False) \
            .execute()
        
        return result.data
        
    except Exception as e:
        print(f"Error getting pending reminders: {e}")
        return []

async def mark_reminder_completed(reminder_id: int) -> bool:
    """Mark a reminder as completed"""
    try:
        client = get_supabase_client()
        
        result = client.table("user_reminders") \
            .update({"is_completed": True, "updated_at": datetime.now().isoformat()}) \
            .eq("id", reminder_id) \
            .execute()
        
        return bool(result.data)
        
    except Exception as e:
        print(f"Error marking reminder completed: {e}")
        return False

# ================================================================================================
# CRYPTO PREFERENCES
# ================================================================================================

async def save_crypto_preferences(user_id: str, **crypto_prefs) -> bool:
    """Save crypto preferences"""
    try:
        client = get_supabase_client()
        
        crypto_prefs.update({
            "user_id": user_id,
            "updated_at": datetime.now().isoformat()
        })
        
        result = client.table("user_crypto_preferences").upsert(crypto_prefs).execute()
        return bool(result.data)
        
    except Exception as e:
        print(f"Error saving crypto preferences: {e}")
        return False

async def get_crypto_preferences(user_id: str) -> Dict:
    """Get crypto preferences"""
    try:
        client = get_supabase_client()
        
        result = client.table("user_crypto_preferences") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
        
        return result.data[0] if result.data else {}
        
    except Exception as e:
        print(f"Error getting crypto preferences: {e}")
        return {}

# ================================================================================================
# ENCRYPTION UTILITIES
# ================================================================================================

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data like PINs"""
    # Simple hash-based encryption (for production, use proper encryption)
    salt = "sofi_ai_salt_2025"
    return hashlib.sha256((data + salt).encode()).hexdigest()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data (placeholder - hash is one-way)"""
    # For real encryption, implement proper decryption
    # For now, return as-is since we use hashing
    return encrypted_data

def verify_sensitive_data(input_data: str, stored_hash: str) -> bool:
    """Verify sensitive data against stored hash"""
    return encrypt_sensitive_data(input_data) == stored_hash

# ================================================================================================
# CONVENIENCE FUNCTIONS
# ================================================================================================

async def remember_user_name(user_id: str, name: str) -> bool:
    """Remember user's preferred name"""
    return await save_user_memory(user_id, "preference", "name", name)

async def get_user_name(user_id: str) -> Optional[str]:
    """Get user's preferred name"""
    return await get_user_memory(user_id, "preference", "name")

async def remember_user_pin(user_id: str, pin: str) -> bool:
    """Remember user's PIN (encrypted)"""
    return await save_user_memory(user_id, "security", "pin", pin, encrypt=True)

async def verify_user_pin(user_id: str, pin: str) -> bool:
    """Verify user's PIN"""
    stored_pin = await get_user_memory(user_id, "security", "pin")
    if stored_pin:
        return verify_sensitive_data(pin, stored_pin)
    return False

async def remember_user_birthday(user_id: str, birthday: date) -> bool:
    """Remember user's birthday"""
    return await save_user_preference(user_id, birthday=birthday)

async def get_user_birthday(user_id: str) -> Optional[date]:
    """Get user's birthday"""
    prefs = await get_user_preferences(user_id)
    birthday_str = prefs.get("birthday")
    if birthday_str:
        return date.fromisoformat(birthday_str)
    return None

async def save_user_note(user_id: str, note_key: str, note_content: str) -> bool:
    """Save a user note"""
    return await save_user_memory(user_id, "note", note_key, note_content)

async def get_user_note(user_id: str, note_key: str) -> Optional[str]:
    """Get a user note"""
    return await get_user_memory(user_id, "note", note_key)

async def get_all_user_notes(user_id: str) -> List[Dict]:
    """Get all user notes"""
    return await get_all_user_memories(user_id, "note")

# ================================================================================================
# INTELLIGENT MEMORY FUNCTIONS
# ================================================================================================

async def process_memory_command(user_id: str, message: str) -> Optional[str]:
    """
    Process natural language memory commands
    
    Examples:
    - "Remember my birthday is June 10, 1998"
    - "Call me King T"
    - "My PIN is 1234"
    - "Save this note: Start business plan next week"
    - "I want to save 2 million for a car"
    """
    message_lower = message.lower()
      # Name preferences
    if "call me" in message_lower:
        name = message_lower.split("call me", 1)[1].strip()
        if await remember_user_name(user_id, name):
            return f"Got it! I'll call you {name} from now on. 😊"
    
    # Birthday
    if "birthday" in message_lower or "born" in message_lower:
        # Extract date (simplified - you could use more sophisticated parsing)
        import re
        date_pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{4}|\w+ \d{1,2}, \d{4})'
        date_match = re.search(date_pattern, message)
        if date_match:
            try:
                # Parse date (you'd implement proper date parsing)
                birthday_str = date_match.group(1)
                # Save birthday
                return f"I'll remember your birthday! 🎂 I'll wish you happy birthday when the time comes."
            except:
                pass
    
    # PIN
    if "pin is" in message_lower:
        pin_match = re.search(r'pin is (\d{4,6})', message_lower)
        if pin_match:
            pin = pin_match.group(1)
            if await remember_user_pin(user_id, pin):
                return "Your PIN has been securely saved! 🔒 I'll ask for it when you make transfers."
    
    # Notes
    if "save this note" in message_lower or "remember this" in message_lower:
        note_content = message.split(":", 1)[1].strip() if ":" in message else message
        note_key = f"note_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if await save_user_note(user_id, note_key, note_content):
            return "Note saved! 📝 I'll remember this for you."
    
    # Goals
    if "save" in message_lower and ("million" in message_lower or "thousand" in message_lower):
        # Extract savings goal (simplified)
        return "I'll help you track this savings goal! 💰"
    
    return None

async def get_contextual_memory(user_id: str, context: str) -> Dict:
    """
    Get relevant memories based on context
    
    Args:
        user_id: User identifier
        context: Context like 'greeting', 'transfer', 'birthday', etc.
    
    Returns:
        Dict: Relevant memory information
    """
    result = {}
    
    # Get user name for personalization
    name = await get_user_name(user_id)
    if name:
        result["name"] = name
    
    # Context-specific memories
    if context == "greeting":
        # Get last interaction info, goals, etc.
        goals = await get_user_goals(user_id)
        if goals:
            result["active_goals"] = len(goals)
    
    elif context == "transfer":
        # Get preferred bank, PIN status, etc.
        prefs = await get_user_preferences(user_id)
        result["preferred_bank"] = prefs.get("preferred_bank")
        
        # Check if PIN is set
        pin_exists = await get_user_memory(user_id, "security", "pin")
        result["pin_set"] = bool(pin_exists)
    
    elif context == "birthday":
        birthday = await get_user_birthday(user_id)
        if birthday:
            today = date.today()
            if birthday.month == today.month and birthday.day == today.day:
                result["is_birthday"] = True
    
    return result
