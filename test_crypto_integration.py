import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the crypto modules
from crypto.wallet import create_bitnob_wallet, get_user_wallet_addresses, get_wallet_balance
from crypto.rates import get_crypto_to_ngn_rate, get_multiple_crypto_rates, format_crypto_rates_message
from main import handle_crypto_commands, generate_ai_reply

class TestCryptoIntegration:
    """Test suite for crypto integration functionality"""    @patch.dict(os.environ, {'BITNOB_SECRET_KEY': 'test_key'})
    @patch('crypto.wallet.requests.post')
    def test_create_bitnob_wallet_success(self, mock_post):
        """Test successful wallet creation"""
        # Mock successful Bitnob API response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "data": {
                "id": "wallet_123",
                "customerEmail": "user123@sofiwallet.com",
                "currency": "NGN",
                "balance": 0
            }
        }
        mock_post.return_value = mock_response
        
        # Test wallet creation
        result = create_bitnob_wallet("user123", "test@example.com")
        
        assert "data" in result
        assert result["data"]["id"] == "wallet_123"
        assert result["data"]["customerEmail"] == "user123@sofiwallet.com"

    @patch.dict(os.environ, {'BITNOB_SECRET_KEY': 'test_key'})
    @patch('crypto.wallet.requests.post')
    def test_create_bitnob_wallet_error(self, mock_post):
        """Test wallet creation error handling"""
        # Mock API error
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response
        
        result = create_bitnob_wallet("user123")
        
        assert "error" in result
        assert "API error" in result["error"]

    @patch('crypto.rates.requests.get')
    def test_get_crypto_to_ngn_rate_success(self, mock_get):
        """Test successful crypto rate fetching"""
        # Mock CoinGecko API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bitcoin": {"ngn": 55000000.50}
        }
        mock_get.return_value = mock_response
        
        rate = get_crypto_to_ngn_rate("BTC")
        
        assert rate == 55000000.50
        mock_get.assert_called_once()

    @patch('crypto.rates.requests.get')
    def test_get_multiple_crypto_rates(self, mock_get):
        """Test fetching multiple crypto rates"""
        # Mock CoinGecko API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "bitcoin": {"ngn": 55000000.50},
            "ethereum": {"ngn": 4200000.75},
            "tether": {"ngn": 1650.25}
        }
        mock_get.return_value = mock_response
        
        rates = get_multiple_crypto_rates(["BTC", "ETH", "USDT"])
        
        assert "BTC" in rates
        assert "ETH" in rates
        assert "USDT" in rates
        assert rates["BTC"] == 55000000.50

    def test_format_crypto_rates_message(self):
        """Test crypto rates message formatting"""
        rates = {
            "BTC": 55000000.50,
            "ETH": 4200000.75,
            "USDT": 1650.25
        }
        
        message = format_crypto_rates_message(rates)
        
        assert "BTC" in message
        assert "ETH" in message
        assert "USDT" in message
        assert "₦55,000,000.50" in message
        assert "Current Crypto Rates" in message

    def test_handle_crypto_commands_create_wallet(self):
        """Test crypto wallet creation command handling"""
        user_data = {
            "id": "user123",
            "first_name": "John",
            "email": "john@example.com"
        }
        
        with patch('main.create_bitnob_wallet') as mock_create:
            mock_create.return_value = {
                "data": {
                    "id": "wallet_123",
                    "customerEmail": "user123@sofiwallet.com"
                }
            }
            
            response = handle_crypto_commands("chat123", "create wallet", user_data)
            
            assert response is not None
            assert "Crypto Wallet Created Successfully" in response
            assert "John" in response
            assert "wallet_123" in response
            mock_create.assert_called_once()

    def test_handle_crypto_commands_wallet_addresses(self):
        """Test wallet addresses command handling"""
        user_data = {
            "id": "user123",
            "first_name": "John"
        }
        
        with patch('main.get_user_wallet_addresses') as mock_get_addresses:
            mock_get_addresses.return_value = {
                "addresses": {
                    "BTC": {
                        "address": "bc1qxyz123...",
                        "balance": 0.001,
                        "wallet_id": "wallet_123"
                    },
                    "ETH": {
                        "address": "0xabc456...",
                        "balance": 0.5,
                        "wallet_id": "wallet_456"
                    }
                }
            }
            
            response = handle_crypto_commands("chat123", "my wallet addresses", user_data)
            
            assert response is not None
            assert "John's Crypto Wallet Addresses" in response
            assert "BTC" in response
            assert "ETH" in response
            assert "bc1qxyz123" in response
            assert "0xabc456" in response

    def test_handle_crypto_commands_crypto_rates(self):
        """Test crypto rates command handling"""
        user_data = {"id": "user123", "first_name": "John"}
        
        with patch('main.get_multiple_crypto_rates') as mock_get_rates:
            with patch('main.format_crypto_rates_message') as mock_format:
                mock_get_rates.return_value = {"BTC": 55000000.50}
                mock_format.return_value = "💹 Current Crypto Rates: BTC ₦55,000,000.50"
                
                response = handle_crypto_commands("chat123", "crypto rates", user_data)
                
                assert response is not None
                assert "Current Crypto Rates" in response
                mock_get_rates.assert_called_once()
                mock_format.assert_called_once()

    def test_handle_crypto_commands_no_user_data(self):
        """Test crypto commands without user data"""
        response = handle_crypto_commands("chat123", "create wallet", None)
        
        assert response is not None
        assert "complete onboarding first" in response.lower()

    def test_handle_crypto_commands_unknown_command(self):
        """Test unknown crypto command"""
        user_data = {"id": "user123", "first_name": "John"}
        
        response = handle_crypto_commands("chat123", "transfer money", user_data)
        
        assert response is None  # Should return None for non-crypto commands

    @pytest.mark.asyncio
    @patch('main.check_virtual_account')
    @patch('main.supabase')
    @patch('main.handle_crypto_commands')
    async def test_crypto_integration_in_ai_reply(self, mock_handle_crypto, mock_supabase, mock_check_va):
        """Test crypto command integration in AI reply generation"""
        # Mock onboarded user
        mock_check_va.return_value = {"accountnumber": "1234567890"}
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "user123", "first_name": "John"}
        ]
        
        # Mock crypto command response
        mock_handle_crypto.return_value = "🎉 Crypto Wallet Created Successfully!"
        
        with patch('main.save_chat_message') as mock_save:
            with patch('main.send_reply') as mock_send:
                mock_save.return_value = AsyncMock()
                
                response = await generate_ai_reply("chat123", "create crypto wallet")
                
                assert response == "🎉 Crypto Wallet Created Successfully!"
                mock_handle_crypto.assert_called_once()
                mock_send.assert_called_once()

    def test_crypto_webhook_route_integration(self):
        """Test that crypto webhook route is properly integrated"""
        from main import app
        
        # Check if the crypto webhook route exists
        with app.test_client() as client:
            # Test that the route exists (will return 400 for empty data, but route exists)
            response = client.post('/crypto/webhook', json={})
            
            # Should not return 404 (route exists)
            assert response.status_code != 404

    def test_crypto_api_routes_integration(self):
        """Test that crypto API routes are properly integrated"""
        from main import app
        
        with app.test_client() as client:
            # Test create wallet endpoint
            response = client.get('/create_crypto_wallet/user123')
            assert response.status_code != 404
            
            # Test rates endpoint
            response = client.get('/crypto/rates')
            assert response.status_code != 404
            
            # Test user wallet endpoint
            response = client.get('/user/user123/wallet')
            assert response.status_code != 404

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
