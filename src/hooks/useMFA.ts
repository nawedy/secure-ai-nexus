import { useState, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { MFASetup, MFAVerification } from '@/types/auth';
import { logSecurityEvent } from '@/services/security';
import { generateTOTP, verifyTOTP } from '@/utils/totp';

interface MFAError {
  code: string;
  message: string;
}

export const useMFA = () => {
  const { user, updateUser } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<MFAError | null>(null);

  const setupMFA = useCallback(async (): Promise<MFASetup> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/mfa/setup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message);
      }

      const setupData = await response.json();

      await logSecurityEvent({
        type: 'MFA_SETUP_INITIATED',
        userId: user?.id,
        details: 'MFA setup process started',
      });

      return setupData;
    } catch (err) {
      const error = err as Error;
      setError({
        code: 'SETUP_FAILED',
        message: error.message || 'Failed to setup MFA',
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  const verifyAndEnableMFA = useCallback(async (verification: MFAVerification): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/mfa/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(verification),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message);
      }

      await updateUser({ mfaEnabled: true, mfaVerified: true });

      await logSecurityEvent({
        type: 'MFA_ENABLED',
        userId: user?.id,
        details: 'MFA successfully enabled and verified',
      });
    } catch (err) {
      const error = err as Error;
      setError({
        code: 'VERIFICATION_FAILED',
        message: error.message || 'Failed to verify MFA code',
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [user, updateUser]);

  const verifyMFACode = useCallback(async (code: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/mfa/verify-code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message);
      }

      const { valid } = await response.json();

      await logSecurityEvent({
        type: valid ? 'MFA_VERIFICATION_SUCCESS' : 'MFA_VERIFICATION_FAILED',
        userId: user?.id,
        details: `MFA code verification ${valid ? 'succeeded' : 'failed'}`,
      });

      return valid;
    } catch (err) {
      const error = err as Error;
      setError({
        code: 'VERIFICATION_FAILED',
        message: error.message || 'Failed to verify MFA code',
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  const disableMFA = useCallback(async (verificationCode: string): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // First verify the code before disabling
      const isValid = await verifyMFACode(verificationCode);
      
      if (!isValid) {
        throw new Error('Invalid verification code');
      }

      const response = await fetch('/api/auth/mfa/disable', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ verificationCode }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message);
      }

      await updateUser({ mfaEnabled: false, mfaVerified: false });

      await logSecurityEvent({
        type: 'MFA_DISABLED',
        userId: user?.id,
        details: 'MFA disabled',
        severity: 'high',
      });
    } catch (err) {
      const error = err as Error;
      setError({
        code: 'DISABLE_FAILED',
        message: error.message || 'Failed to disable MFA',
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [user, updateUser, verifyMFACode]);

  const generateRecoveryCodes = useCallback(async (): Promise<string[]> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/mfa/recovery-codes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message);
      }

      const { codes } = await response.json();

      await logSecurityEvent({
        type: 'MFA_RECOVERY_CODES_GENERATED',
        userId: user?.id,
        details: 'New MFA recovery codes generated',
      });

      return codes;
    } catch (err) {
      const error = err as Error;
      setError({
        code: 'RECOVERY_CODES_FAILED',
        message: error.message || 'Failed to generate recovery codes',
      });
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  return {
    setupMFA,
    verifyAndEnableMFA,
    verifyMFACode,
    disableMFA,
    generateRecoveryCodes,
    isLoading,
    error,
  };
}; 