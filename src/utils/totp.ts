import { authenticator } from 'otplib';
import { createHash } from 'crypto';
import * as qrcode from 'qrcode';

// Configure TOTP settings
authenticator.options = {
  window: 1, // Allow 1 step before/after for time drift
  step: 30, // 30-second step
  digits: 6, // 6-digit codes
};

interface TOTPSecret {
  secret: string;
  uri: string;
  qrCode: string;
}

export const generateTOTP = async (
  userId: string,
  issuer: string = 'SecureAI Platform'
): Promise<TOTPSecret> => {
  // Generate a secure random secret
  const secret = authenticator.generateSecret();

  // Create an otpauth URL for QR codes
  const uri = authenticator.keyuri(
    userId,
    issuer,
    secret
  );

    const qrCode = await qrcode.toDataURL(uri)

  return {
    secret,
    uri,
    qrCode,
  };
};

export const verifyTOTP = (
  token: string,
  secret: string,
  options?: {
    window?: number;
    time?: number;
  }
): boolean => {
  try {
    if (options?.window) {
      authenticator.options = { ...authenticator.options, window: options.window };
    }

    return authenticator.verify({
      token,
      secret,
      ...(options?.time && { time: options.time }),
    });
  } catch (error) {
    console.error('TOTP verification error:', error);
    return false;
  }
};

export const hashSecret = (secret: string): string => {
  return createHash('sha256')
    .update(secret)
    .digest('hex');
};

export const generateBackupCode = (): string => {
  const code = authenticator.generateSecret(20); // 20 bytes = 40 hex chars
  return code.match(/.{1,4}/g)?.join('-') || code; // Format as XXXX-XXXX-XXXX-XXXX-XXXX
};

export const validateTOTPSetup = (
  secret: string,
  token: string
): { valid: boolean; error?: string } => {
  try {
    if (!secret || !token) {
      return {
        valid: false,
        error: 'Missing required parameters',
      };
    }

    // Check if the token matches the expected format
    if (!/^\d{6}$/.test(token)) {
      return {
        valid: false,
        error: 'Invalid token format',
      };
    }

    // Verify with a slightly larger window during setup
    const isValid = verifyTOTP(token, secret, { window: 2 });

    return {
      valid: isValid,
      ...(isValid ? {} : { error: 'Invalid verification code' }),
    };
  } catch (error) {
    console.error('TOTP setup validation error:', error);
    return {
      valid: false,
      error: 'Validation failed',
    };
  }
};

export const generateEmergencyAccessToken = (
  userId: string,
  expiresIn: number = 300 // 5 minutes in seconds
): string => {
  const secret = authenticator.generateSecret();
  const timestamp = Math.floor(Date.now() / 1000);
  const expiryTimestamp = timestamp + expiresIn;

  const token = createHash('sha256')
    .update(`${userId}:${secret}:${expiryTimestamp}`)
    .digest('hex');

  return `${token}.${expiryTimestamp}`;
}; 