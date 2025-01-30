import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useMFA } from '@/hooks/useMFA';
import { useNotifications } from '@/hooks/useNotifications';

export const SecuritySettings: React.FC = () => {
  const { user, updateSecuritySettings } = useAuth();
  const { setupMFA, disableMFA, verifyMFACode } = useMFA();
  const { notify } = useNotifications();
  const [mfaCode, setMFACode] = useState('');
  const [loading, setLoading] = useState(false);

  const handleMFAToggle = async () => {
    setLoading(true);
    try {
      if (user?.mfaEnabled) {
        await disableMFA();
        notify('MFA disabled successfully', 'success');
      } else {
        const response = await setupMFA();
        // Show QR code modal
        notify('Scan the QR code to enable MFA', 'info');
      }
    } catch (error) {
      notify('Error updating MFA settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyMFA = async () => {
    try {
      await verifyMFACode(mfaCode);
      notify('MFA verified successfully', 'success');
    } catch (error) {
      notify('Invalid MFA code', 'error');
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Security Settings</h2>

      <div className="bg-white shadow rounded-lg divide-y divide-gray-200">
        {/* MFA Section */}
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                Multi-Factor Authentication
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Add an extra layer of security to your account
              </p>
            </div>
            <button
              onClick={handleMFAToggle}
              disabled={loading}
              className={`${
                user?.mfaEnabled
                  ? 'bg-red-600 hover:bg-red-700'
                  : 'bg-green-600 hover:bg-green-700'
              } text-white px-4 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50`}
            >
              {loading
                ? 'Processing...'
                : user?.mfaEnabled
                ? 'Disable MFA'
                : 'Enable MFA'}
            </button>
          </div>

          {/* MFA Verification Input */}
          {user?.mfaEnabled && (
            <div className="mt-4">
              <input
                type="text"
                value={mfaCode}
                onChange={(e) => setMFACode(e.target.value)}
                placeholder="Enter MFA Code"
                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
              <button
                onClick={handleVerifyMFA}
                className="mt-2 bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Verify Code
              </button>
            </div>
          )}
        </div>

        {/* Session Management */}
        <div className="p-6">
          <h3 className="text-lg font-medium text-gray-900">Active Sessions</h3>
          <div className="mt-4 space-y-4">
            {/* List active sessions */}
          </div>
        </div>

        {/* Security Log */}
        <div className="p-6">
          <h3 className="text-lg font-medium text-gray-900">Security Log</h3>
          <div className="mt-4 space-y-4">
            {/* List security events */}
          </div>
        </div>
      </div>
    </div>
  );
}; 