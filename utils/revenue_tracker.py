#!/usr/bin/env python3
"""
Sofi AI Revenue Tracking System
================================

This module handles all revenue tracking and fee collection:
1. Transfer fees (₦50 per transfer)
2. Deposit fees (₦10 per bank deposit)
3. Crypto trading profits (₦500-1000 markup)
4. Airtime/Data profits (markup on cost price)
"""

import logging
from datetime import datetime
from typing import Dict, Optional
import uuid

logger = logging.getLogger(__name__)

# Revenue Configuration
TRANSFER_FEE = 50.0  # ₦50 per transfer
DEPOSIT_FEE = 10.0   # ₦10 per bank deposit
CRYPTO_MARKUP_BTC = 1000.0   # ₦1000 markup for BTC
CRYPTO_MARKUP_USDT = 500.0   # ₦500 markup for USDT
CRYPTO_MARKUP_ETH = 750.0    # ₦750 markup for ETH

# Airtime/Data markup percentages
AIRTIME_MARKUP_PERCENT = 2.5  # 2.5% markup on cost price
DATA_MARKUP_PERCENT = 3.0     # 3.0% markup on cost price

class RevenueTracker:
    """Handles all revenue tracking and fee collection"""
    
    def __init__(self, supabase_client):
        self.client = supabase_client
    
    def log_transfer_fee(self, chat_id: str, user_id: str, transfer_amount: float, 
                        monnify_reference: str, recipient_account: str, 
                        recipient_bank: str) -> bool:
        """Log transfer fee when user makes a transfer"""
        try:
            fee_data = {
                "telegram_chat_id": str(chat_id),
                "user_id": user_id,
                "transfer_amount": transfer_amount,
                "fee_charged": TRANSFER_FEE,
                "monnify_reference": monnify_reference,
                "recipient_account": recipient_account,
                "recipient_bank": recipient_bank,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.client.table("transfer_charges").insert(fee_data).execute()
            
            if result.data:
                logger.info(f"Transfer fee logged: ₦{TRANSFER_FEE} for transfer {monnify_reference}")
                return True
            else:
                logger.error(f"Failed to log transfer fee: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error logging transfer fee: {str(e)}")
            return False
    
    def log_deposit_fee(self, chat_id: str, user_id: str, deposit_amount: float, 
                       monnify_reference: str) -> bool:
        """Log deposit fee when user receives bank deposit"""
        try:
            fee_data = {
                "telegram_chat_id": str(chat_id),
                "user_id": user_id,
                "deposit_amount": deposit_amount,
                "fee_charged": DEPOSIT_FEE,
                "monnify_reference": monnify_reference,
                "deposit_source": "bank_transfer",
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.client.table("deposit_fees").insert(fee_data).execute()
            
            if result.data:
                logger.info(f"Deposit fee logged: ₦{DEPOSIT_FEE} for deposit {monnify_reference}")
                return True
            else:
                logger.error(f"Failed to log deposit fee: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error logging deposit fee: {str(e)}")
            return False
    
    def log_crypto_trade(self, chat_id: str, user_id: str, crypto_type: str, 
                        crypto_amount: float, naira_equivalent: float, 
                        conversion_rate: float, bitnob_tx_id: str = None) -> bool:
        """Log crypto trade with profit calculation"""
        try:
            # Calculate profit based on crypto type
            profit_markup = {
                'BTC': CRYPTO_MARKUP_BTC,
                'USDT': CRYPTO_MARKUP_USDT,
                'ETH': CRYPTO_MARKUP_ETH,
                'USDC': CRYPTO_MARKUP_USDT  # Same as USDT
            }.get(crypto_type, CRYPTO_MARKUP_USDT)
            
            trade_data = {
                "telegram_chat_id": str(chat_id),
                "user_id": user_id,
                "crypto_type": crypto_type,
                "crypto_amount": crypto_amount,
                "naira_equivalent": naira_equivalent,
                "conversion_rate_used": conversion_rate,
                "profit_made_on_trade": profit_markup,
                "bitnob_transaction_id": bitnob_tx_id,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.client.table("crypto_trades").insert(trade_data).execute()
            
            if result.data:
                logger.info(f"Crypto trade logged: {crypto_amount} {crypto_type} → ₦{naira_equivalent} (Profit: ₦{profit_markup})")
                return True
            else:
                logger.error(f"Failed to log crypto trade: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error logging crypto trade: {str(e)}")
            return False
    
    def log_airtime_sale(self, chat_id: str, user_id: str, network: str, 
                        phone_number: str, amount_sold: float, cost_price: float,
                        nellobytes_ref: str = None) -> bool:
        """Log airtime sale with profit calculation"""
        try:
            # Calculate sale price with markup
            sale_price = cost_price * (1 + AIRTIME_MARKUP_PERCENT / 100)
            
            airtime_data = {
                "telegram_chat_id": str(chat_id),
                "user_id": user_id,
                "network": network.lower(),
                "phone_number": phone_number,
                "amount_sold": amount_sold,
                "sale_price": sale_price,
                "cost_price": cost_price,
                "nellobytes_reference": nellobytes_ref,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.client.table("airtime_sales").insert(airtime_data).execute()
            
            if result.data:
                profit = sale_price - cost_price
                logger.info(f"Airtime sale logged: ₦{amount_sold} {network} (Profit: ₦{profit:.2f})")
                return True
            else:
                logger.error(f"Failed to log airtime sale: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error logging airtime sale: {str(e)}")
            return False
    
    def log_data_sale(self, chat_id: str, user_id: str, network: str, 
                     phone_number: str, bundle_size: str, amount_sold: float, 
                     cost_price: float, nellobytes_ref: str = None) -> bool:
        """Log data sale with profit calculation"""
        try:
            # Calculate sale price with markup
            sale_price = cost_price * (1 + DATA_MARKUP_PERCENT / 100)
            
            data_data = {
                "telegram_chat_id": str(chat_id),
                "user_id": user_id,
                "network": network.lower(),
                "phone_number": phone_number,
                "bundle_size": bundle_size,
                "amount_sold": amount_sold,
                "sale_price": sale_price,
                "cost_price": cost_price,
                "nellobytes_reference": nellobytes_ref,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            result = self.client.table("data_sales").insert(data_data).execute()
            
            if result.data:
                profit = sale_price - cost_price
                logger.info(f"Data sale logged: {bundle_size} {network} (Profit: ₦{profit:.2f})")
                return True
            else:
                logger.error(f"Failed to log data sale: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error logging data sale: {str(e)}")
            return False
    
    def get_financial_summary(self) -> Dict:
        """Get current financial summary"""
        try:
            result = self.client.table("sofi_financial_summary").select("*").execute()
            
            if result.data:
                summary = result.data[0]
                return {
                    "total_revenue": float(summary.get("total_revenue", 0)),
                    "crypto_profit": float(summary.get("total_crypto_profit", 0)),
                    "transfer_revenue": float(summary.get("total_transfer_revenue", 0)),
                    "airtime_revenue": float(summary.get("total_airtime_revenue", 0)),
                    "data_revenue": float(summary.get("total_data_revenue", 0)),
                    "deposit_fees": float(summary.get("total_deposit_fee_collected", 0)),
                    "crypto_usdt_received": float(summary.get("total_crypto_received_usdt", 0)),
                    "crypto_btc_received": float(summary.get("total_crypto_received_btc", 0)),
                    "airtime_sold": float(summary.get("total_airtime_amount_sold", 0)),
                    "data_sold": float(summary.get("total_data_amount_sold", 0)),
                    "personal_withdrawals": float(summary.get("total_personal_withdrawal", 0)),
                    "last_updated": summary.get("last_updated")
                }
            else:
                return {"error": "No financial summary found"}
                
        except Exception as e:
            logger.error(f"Error getting financial summary: {str(e)}")
            return {"error": str(e)}
    
    def log_personal_withdrawal(self, amount: float, description: str = "Personal withdrawal") -> bool:
        """Log when ThankGod withdraws profit"""
        try:
            # Update the personal withdrawal total
            result = self.client.table("sofi_financial_summary").update({
                "total_personal_withdrawal": self.client.table("sofi_financial_summary").select("total_personal_withdrawal").execute().data[0]["total_personal_withdrawal"] + amount,
                "last_updated": datetime.now().isoformat()
            }).execute()
            
            if result.data:
                logger.info(f"Personal withdrawal logged: ₦{amount} - {description}")
                return True
            else:
                logger.error(f"Failed to log personal withdrawal: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Error logging personal withdrawal: {str(e)}")
            return False

# Fee calculation helpers
def calculate_transfer_fee(amount: float) -> float:
    """Calculate transfer fee (fixed ₦50)"""
    return TRANSFER_FEE

def calculate_deposit_fee(amount: float) -> float:
    """Calculate deposit fee (fixed ₦10)"""
    return DEPOSIT_FEE

def calculate_crypto_profit(crypto_type: str, amount: float) -> float:
    """Calculate crypto trading profit"""
    return {
        'BTC': CRYPTO_MARKUP_BTC,
        'USDT': CRYPTO_MARKUP_USDT,
        'ETH': CRYPTO_MARKUP_ETH,
        'USDC': CRYPTO_MARKUP_USDT
    }.get(crypto_type, CRYPTO_MARKUP_USDT)

def calculate_airtime_markup(cost_price: float) -> float:
    """Calculate airtime sale price with markup"""
    return cost_price * (1 + AIRTIME_MARKUP_PERCENT / 100)

def calculate_data_markup(cost_price: float) -> float:
    """Calculate data sale price with markup"""
    return cost_price * (1 + DATA_MARKUP_PERCENT / 100)
