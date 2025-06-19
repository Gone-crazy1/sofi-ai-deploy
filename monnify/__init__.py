"""
Monnify Integration Module for Sofi AI Banking Service
Official Banking Partner: Monnify

This module provides complete banking integration including:
- Virtual account creation
- Bank transfers and disbursements
- Transaction verification
- Webhook handling
- Balance management
"""

from .monnify_api import MonnifyAPI
from .monnify_webhook import MonnifyWebhookHandler, handle_monnify_webhook

__all__ = [
    'MonnifyAPI',
    'MonnifyWebhookHandler', 
    'handle_monnify_webhook'
]

__version__ = '1.0.0'
__author__ = 'Sofi AI Team'
__description__ = 'Official Monnify Banking Integration for Sofi AI'
