export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  role: 'user' | 'admin';
  mfaEnabled: boolean;
  mfaVerified: boolean;
  lastLogin: string;
  securityLevel: 'standard' | 'enhanced';
  permissions: string[];
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  mfaRequired: boolean;
  mfaVerified: boolean;
  sessionExpiry: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface MFAVerification {
  code: string;
  sessionToken: string;
}

export interface SecurityQuestion {
  id: string;
  question: string;
  answer: string;
}

export interface AuthError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface MFASetup {
  qrCode: string;
  secret: string;
  backupCodes: string[];
}

export interface MFAStatus {
  enabled: boolean;
  verified: boolean;
  lastVerified: string | null;
  recoveryCodesRemaining: number;
}

export interface SecurityEvent {
  id: string;
  type: string;
  details: string;
  userId: string;
  timestamp: string;
  metadata?: Record<string, any>;
  severity: 'low' | 'medium' | 'high' | 'critical';
} 