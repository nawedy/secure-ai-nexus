import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/router';
import { QRCodeDisplay } from '@/components/auth/QRCodeDisplay';
import { Alert } from '@/components/ui/Alert';
import { BackupCodeDisplay } from '@/components/auth/BackupCodeDisplay';
import { useMFA } from '@/hooks/useMFA';
import { MFASetup } from '@/types/auth';
import { logSecurityEvent } from '@/services/security';

export default function MFASetupPage() {
  const { user } = useAuth();
  const router = useRouter();
  const { setupMFA, verifyAndEnableMFA } = useMFA();
  const [setupData, setSetupData] = useState<MFASetup | null>(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'qr' | 'verify' | 'backup'>('qr');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) {
      router.push('/auth/login');
      return;
    }

    if (user.mfaEnabled) {
      router.push('/dashboard');
      return;
    }

    initializeMFASetup();
  }, [user, router]);

  const initializeMFASetup = async () => {
    try {
      setLoading(true);
      const data = await setupMFA();
      setSetupData(data);
      
      await logSecurityEvent({
        type: 'MFA_SETUP_INITIATED',
        userId: user?.id,
        details: 'MFA setup process started',
      });
    } catch (error) {
      setError('Failed to initialize MFA setup. Please try again.');
      console.error('MFA setup error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVerification = async () => {
    if (!setupData) return;

    try {
      setLoading(true);
      setError(null);

      await verifyAndEnableMFA({
        code: verificationCode,
        secret: setupData.secret,
      });

      await logSecurityEvent({
        type: 'MFA_SETUP_COMPLETED',
        userId: user?.id,
        details: 'MFA successfully enabled',
      });

      setStep('backup');
    } catch (error) {
      setError('Invalid verification code. Please try again.');
      await logSecurityEvent({
        type: 'MFA_SETUP_FAILED',
        userId: user?.id,
        details: 'Failed verification attempt during MFA setup',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleComplete = async () => {
    await logSecurityEvent({
      type: 'MFA_SETUP_BACKUP_SAVED',
      userId: user?.id,
      details: 'Backup codes generated and saved',
    });
    router.push('/dashboard');
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="text-center text-3xl font-extrabold text-gray-900">
          Set Up Two-Factor Authentication
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Enhance your account security
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error && (
            <Alert type="error" message={error} className="mb-4" />
          )}

          {step === 'qr' && setupData && (
            <>
              <div className="text-center mb-6">
                <h3 className="text-lg font-medium text-gray-900">
                  Scan QR Code
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  Scan this QR code with your authenticator app
                </p>
              </div>

              <QRCodeDisplay
                uri={setupData.qrCode}
                className="mx-auto mb-6"
              />

              <div className="space-y-4">
                <div>
                  <label htmlFor="code" className="block text-sm font-medium text-gray-700">
                    Enter Verification Code
                  </label>
                  <input
                    type="text"
                    id="code"
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value)}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    maxLength={6}
                    placeholder="000000"
                  />
                </div>

                <button
                  onClick={handleVerification}
                  disabled={verificationCode.length !== 6}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  Verify Code
                </button>
              </div>
            </>
          )}

          {step === 'backup' && setupData && (
            <BackupCodeDisplay
              codes={setupData.backupCodes}
              onComplete={handleComplete}
            />
          )}
        </div>
      </div>
    </div>
  );
} 