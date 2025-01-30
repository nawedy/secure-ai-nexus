export interface BackupCode {
  code: string;
  used: boolean;
  usedAt?: string;
  hashedValue: string;
}

export interface BackupCodesState {
  codes: BackupCode[];
  generatedAt: string;
  lastUsed?: string;
  remainingCodes: number;
}

export interface BackupCodesValidation {
  valid: boolean;
  used: boolean;
  error?: string;
}

export interface BackupCodesGenerationOptions {
  numberOfCodes?: number;
  codeLength?: number;
  format?: 'groups' | 'single';
  groupSize?: number;
} 