import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/router';
import { useForm } from 'react-hook-form';
import { MFAVerification } from '@/types/auth';
import { SecurityIcon, ShieldCheckIcon } from '@/components/icons';
import { Alert } from '@/components/ui/Alert';
import { QRCodeDisplay } from '@/components/auth/QRCodeDisplay';
import { CountdownTimer } from '@/components/auth/CountdownTimer';

export default function MFAVerificationPage() {
  const { verifyMFA, isLoading, user } = useAuth();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [remainingAttempts, setRemainingAttempts] = useState(3);
  const [isBlocked, setIsBlocked] = useState(false);
  const [blockEndTime, setBlockEndTime] = useState<Date | null>(null);
  const { register, handleSubmit, reset, formState: { errors } } = useForm<MFAVerification>();

  // Check if user is already verified
  useEffect(() => {
    if (user?.mfaVerified) {
      router.push('/dashboard');
    }
  }, [user, router]);

  // Handle MFA verification attempts
  const handleVerification = async (data: MFAVerification) => {
    if (isBlocked) return;

    try {
      setError(null);
      await verifyMFA({
        code: data.code,
        sessionToken: sessionStorage.getItem('temp_session_token') || '',
      });
      // Success is handled by AuthContext (redirect to dashboard)
    } catch (err) {
      setRemainingAttempts(prev => prev - 1);
      if (remainingAttempts <= 1) {
        handleTooManyAttempts();
      }
      setError(err instanceof Error ? err.message : 'Verification failed');
      reset(); // Clear the form
    }
  };

  // Handle blocking after too many attempts
  const handleTooManyAttempts = () => {
    setIsBlocked(true);
    const endTime = new Date();
    endTime.setMinutes(endTime.getMinutes() + 15); // 15-minute block
    setBlockEndTime(endTime);
    
    // Log security event
    logSecurityEvent({
      type: 'MFA_BLOCKED',
      details: 'Too many failed attempts',
      userId: user?.id,
    });
  };

  // Handle block timer completion
  const handleBlockEnd = () => {
    setIsBlocked(false);
    setRemainingAttempts(3);
    setBlockEndTime(null);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <SecurityIcon className="mx-auto h-12 w-12 text-indigo-600" />
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Two-Factor Authentication
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Enter the verification code from your authenticator app
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error && (
            <Alert 
              type="error" 
              message={error} 
              className="mb-4"
              details={`Remaining attempts: ${remainingAttempts}`}
            />
          )}

          {isBlocked && blockEndTime && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <h3 className="text-red-800 font-medium">Account Temporarily Locked</h3>
              <p className="text-red-600 text-sm mt-1">
                Too many failed attempts. Please try again in:
              </p>
              <CountdownTimer 
                endTime={blockEndTime} 
                onComplete={handleBlockEnd}
                className="text-red-800 font-mono text-lg mt-2"
              />
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit(handleVerification)}>
            <div>
              <label htmlFor="code" className="block text-sm font-medium text-gray-700">
                Verification Code
              </label>
              <div className="mt-1">
                <input
                  id="code"
                  type="text"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  required
                  maxLength={6}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm font-mono tracking-widest"
                  {...register('code', {
                    required: 'Code is required',
                    pattern: {
                      value: /^[0-9]{6}$/,
                      message: 'Must be a 6-digit number',
                    },
                  })}
                  disabled={isBlocked}
                />
                {errors.code && (
                  <p className="mt-2 text-sm text-red-600">{errors.code.message}</p>
                )}
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={isLoading || isBlocked}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {isLoading ? (
                  <span className="flex items-center">
                    <ShieldCheckIcon className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" />
                    Verifying...
                  </span>
                ) : (
                  'Verify Code'
                )}
              </button>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">
                  Security Information
                </span>
              </div>
            </div>

            <div className="mt-6 text-xs text-gray-500 space-y-2">
              <p>• Enter the 6-digit code from your authenticator app</p>
              <p>• Codes refresh every 30 seconds</p>
              <p>• Three failed attempts will temporarily lock your account</p>
              <p>• All verification attempts are logged and monitored</p>
            </div>
          </div>

          <div className="mt-6">
            <button
              type="button"
              onClick={() => router.push('/auth/mfa/help')}
              className="w-full text-sm text-indigo-600 hover:text-indigo-500"
            >
              Need help accessing your account?
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 