import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { AuthState, User, LoginCredentials, MFAVerification, AuthError } from '@/types/auth';
import { useRouter } from 'next/router';

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  verifyMFA: (verification: MFAVerification) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  updateProfile: (data: Partial<User>) => Promise<void>;
}

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  mfaRequired: true, // Always required
  mfaVerified: false,
  sessionExpiry: null,
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState);
  const router = useRouter();

  useEffect(() => {
    checkAuthStatus();
  }, []);

  useEffect(() => {
    // Set up session refresh interval
    const refreshInterval = setInterval(() => {
      if (state.isAuthenticated) {
        refreshSession();
      }
    }, 5 * 60 * 1000); // Refresh every 5 minutes

    return () => clearInterval(refreshInterval);
  }, [state.isAuthenticated]);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('/api/auth/status');
      const data = await response.json();

      if (data.isAuthenticated) {
        dispatch({ type: 'SET_USER', payload: data.user });
        if (!data.mfaVerified) {
          router.push('/auth/mfa');
        }
      } else {
        dispatch({ type: 'CLEAR_AUTH' });
        router.push('/auth/login');
      }
    } catch (error) {
      console.error('Auth status check failed:', error);
      dispatch({ type: 'CLEAR_AUTH' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const login = async (credentials: LoginCredentials) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message);
      }

      dispatch({ type: 'SET_SESSION', payload: data.sessionToken });
      router.push('/auth/mfa'); // Always redirect to MFA
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error as AuthError });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const verifyMFA = async (verification: MFAVerification) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const response = await fetch('/api/auth/mfa/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(verification),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message);
      }

      dispatch({ type: 'SET_MFA_VERIFIED', payload: true });
      dispatch({ type: 'SET_USER', payload: data.user });
      router.push('/dashboard');
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error as AuthError });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const logout = async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
      dispatch({ type: 'CLEAR_AUTH' });
      router.push('/auth/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const refreshSession = async () => {
    try {
      const response = await fetch('/api/auth/refresh');
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message);
      }

      dispatch({ type: 'SET_SESSION', payload: data.sessionToken });
    } catch (error) {
      console.error('Session refresh failed:', error);
      logout();
    }
  };

  const updateProfile = async (data: Partial<User>) => {
    try {
      const response = await fetch('/api/user/profile', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      const updatedUser = await response.json();

      if (!response.ok) {
        throw new Error(updatedUser.message);
      }

      dispatch({ type: 'SET_USER', payload: updatedUser });
    } catch (error) {
      console.error('Profile update failed:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        verifyMFA,
        logout,
        refreshSession,
        updateProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 