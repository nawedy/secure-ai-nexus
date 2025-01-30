export interface TOTPConfig {
  secret: string;
  uri: string;
  qrCode: string;
  backupCodes: string[];
  algorithm: string;
  digits: number;
  step: number;
}

export interface MFAStatus {
  enabled: boolean;
  verified: boolean;
  lastVerified: string | null;
  method: 'totp' | 'backup' | null;
  recoveryCodesRemaining: number;
  lastFailedAttempt?: string;
  failedAttempts: number;
  blockedUntil?: string;
}

export interface MFAVerificationResult {
  success: boolean;
  method?: 'totp' | 'backup';
  timestamp?: string;
  error?: string;
  remainingAttempts?: number;
  blockDuration?: number;
}

export interface MFASettings {
  userId: string;
  secret: string;
  backupCodes: string[];
  lastRotated: string;
  algorithm: string;
  digits: number;
  step: number;
}

export interface MFAChallenge {
  challengeId: string;
  method: 'totp' | 'backup';
  timestamp: string;
  expiresAt: string;
  attempts: number;
  maxAttempts: number;
} 