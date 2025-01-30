import { customAlphabet } from 'nanoid';
import { createHash } from 'crypto';

// Use a custom alphabet for backup codes that's unambiguous
const BACKUP_CODE_ALPHABET = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';
const BACKUP_CODE_LENGTH = 10;
const NUMBER_OF_CODES = 10;

export class BackupCodesManager {
  private static generateSingleCode(): string {
    const nanoid = customAlphabet(BACKUP_CODE_ALPHABET, BACKUP_CODE_LENGTH);
    return nanoid();
  }

  static generateCodes(): string[] {
    const codes: string[] = [];
    while (codes.length < NUMBER_OF_CODES) {
      const code = this.generateSingleCode();
      if (!codes.includes(code)) {
        codes.push(code);
      }
    }
    return codes;
  }

  static hashCode(code: string): string {
    return createHash('sha256')
      .update(code)
      .digest('hex');
  }

  static formatCode(code: string): string {
    // Format code into groups of 5 characters
    return code.match(/.{1,5}/g)?.join('-') || code;
  }

  static validateCode(code: string, hashedCodes: string[]): boolean {
    const normalizedCode = code.replace(/-/g, '').toUpperCase();
    const hashedCode = this.hashCode(normalizedCode);
    return hashedCodes.includes(hashedCode);
  }
}

export interface BackupCodesStorage {
  hashedCodes: string[];
  lastGenerated: string;
  usedCodes: string[];
}

export const storeBackupCodes = async (
  userId: string,
  codes: string[]
): Promise<void> => {
  const hashedCodes = codes.map(code => BackupCodesManager.hashCode(code));
  const storage: BackupCodesStorage = {
    hashedCodes,
    lastGenerated: new Date().toISOString(),
    usedCodes: [],
  };

  // Store in secure backend storage
  await fetch('/api/auth/backup-codes', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      userId,
      codes: storage,
    }),
  });
};

export const validateAndUseBackupCode = async (
  userId: string,
  code: string
): Promise<boolean> => {
  try {
    const response = await fetch('/api/auth/backup-codes/verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userId,
        code,
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to verify backup code');
    }

    const result = await response.json();
    return result.valid;
  } catch (error) {
    console.error('Backup code validation failed:', error);
    return false;
  }
}; 