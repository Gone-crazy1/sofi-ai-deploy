import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const VerifyPin = () => {
  const [pin, setPin] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [transactionData, setTransactionData] = useState(null);
  const [fetchingTransaction, setFetchingTransaction] = useState(true);
  
  const location = useLocation();
  const navigate = useNavigate();
  
  // Extract txn_id from URL
  const getTransactionId = () => {
    const params = new URLSearchParams(location.search);
    return params.get('txn_id');
  };

  // Fetch transaction details on component mount
  useEffect(() => {
    const txnId = getTransactionId();
    if (!txnId) {
      setError('Invalid transaction link');
      setFetchingTransaction(false);
      return;
    }
    
    fetchTransactionDetails(txnId);
  }, [location]);

  const fetchTransactionDetails = async (txnId) => {
    try {
      const response = await fetch('/api/verify-pin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'get_transaction',
          transaction_id: txnId
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setTransactionData(data.transaction);
      } else {
        setError(data.error || 'Transaction not found');
      }
    } catch (err) {
      setError('Failed to load transaction details');
    } finally {
      setFetchingTransaction(false);
    }
  };

  const handlePinSubmit = async (e) => {
    e.preventDefault();
    
    if (pin.length !== 4) {
      setError('Please enter a 4-digit PIN');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const txnId = getTransactionId();
      
      const response = await fetch('/api/verify-pin', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: 'verify_pin',
          transaction_id: txnId,
          pin: pin
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setSuccess('Transfer completed successfully!');
        setTimeout(() => {
          // Redirect to success page or close window
          window.close() || navigate('/');
        }, 2000);
      } else {
        setError(result.error || 'PIN verification failed');
        setPin(''); // Clear PIN on error
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handlePinChange = (e) => {
    const value = e.target.value.replace(/[^0-9]/g, ''); // Only numbers
    if (value.length <= 4) {
      setPin(value);
    }
  };

  if (fetchingTransaction) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600">
        <div className="bg-white rounded-lg p-8 shadow-lg text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading transaction details...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 p-4">
      <div className="bg-white rounded-lg shadow-lg w-full max-w-md p-6">
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-2xl">🔒</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">Verify PIN</h1>
          <p className="text-gray-600 text-sm mt-2">Enter your 4-digit PIN to complete the transfer</p>
        </div>

        {transactionData && (
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-gray-700 mb-3">Transfer Details</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Amount:</span>
                <span className="font-semibold text-red-600">₦{transactionData.amount?.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">To:</span>
                <span className="font-medium">{transactionData.recipient_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Account:</span>
                <span className="font-medium">{transactionData.account_number}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Bank:</span>
                <span className="font-medium">{transactionData.bank}</span>
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4">
            {success}
          </div>
        )}

        <form onSubmit={handlePinSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter your 4-digit PIN
            </label>
            <input
              type="tel"
              inputMode="numeric"
              pattern="[0-9]*"
              value={pin}
              onChange={handlePinChange}
              placeholder="••••"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg text-center text-lg font-bold tracking-widest focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              disabled={loading}
              autoFocus
            />
          </div>

          <button
            type="submit"
            disabled={pin.length !== 4 || loading}
            className="w-full bg-blue-500 text-white py-3 px-4 rounded-lg font-semibold disabled:bg-gray-300 disabled:cursor-not-allowed hover:bg-blue-600 transition-colors"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Verifying...
              </span>
            ) : (
              '🔐 Confirm Transfer'
            )}
          </button>

          <button
            type="button"
            onClick={() => window.close() || navigate('/')}
            className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-200 transition-colors"
          >
            Cancel
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-gray-500">
          🔒 Your PIN is encrypted and secure
        </div>
      </div>
    </div>
  );
};

export default VerifyPin;
