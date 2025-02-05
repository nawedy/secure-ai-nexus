import { goto } from '$app/navigation';
import { writable, derived, type Writable } from 'svelte/store';

// Define the types for User, AuthStore and Credentials
export interface User {
    id: string;
    email: string;
    mfaVerified: boolean;
}

export interface AuthStore {
    user: User | null;
    token: string | null;
    loading: boolean;
    error: string | null;
    mfaRequired: boolean;
}

export type Credentials = {
    email: string;
    password?: string;
};

export const authStore: Writable<AuthStore> = writable({
    user: null,
    token: null,
    loading: false,
    error: null,
    mfaRequired: false,
});

// Store the temporary session token
let tempSessionToken: string | null = null;

export const auth = {
    login: async (credentials: Credentials) => {
        authStore.update((store) => ({ ...store, loading: true, error: null }));
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || 'Login failed');
            }

            const data = await response.json();
            authStore.update((store) => ({
                ...store,
                token: data.access_token,
                user: data.user,
            }));

            if (data.user.mfaVerified) {
                goto('/dashboard');
            } else {
                // Store temporary token for MFA verification
                tempSessionToken = data.temp_session_token;

                goto('/mfa');
            }
        } catch (error) {
            authStore.update((store) => ({ ...store, error: error instanceof Error ? error.message : 'Login failed' }));
        } finally {
            authStore.update((store) => ({ ...store, loading: false }));
        }
    },
    signup: async (credentials: Credentials) => {
        authStore.update((store) => ({ ...store, loading: true, error: null }));
        try {
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(credentials),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || 'Signup failed');
            }

            goto('/login');
        } catch (error) {
            authStore.update((store) => ({ ...store, error: error instanceof Error ? error.message : 'Signup failed' }));
        } finally {
            authStore.update((store) => ({ ...store, loading: false }));
        }
    },
    verifyMFA: async (code: string) => {
        authStore.update((store) => ({ ...store, loading: true, error: null }));
        try {
            const response = await fetch('/api/auth/verify-mfa', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code, sessionToken: tempSessionToken }),
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || 'MFA Verification failed');
            }

            authStore.update((store) => ({ ...store, user: { ...store.user, mfaVerified: true } }));
            goto('/dashboard');
        } catch (error) {
            authStore.update((store) => ({ ...store, error: error instanceof Error ? error.message : 'MFA Verification failed' }));
        } finally {
            authStore.update((store) => ({ ...store, loading: false }));
        }
    },
    logout: async () => {
        authStore.update((store) => ({ ...store, user: null, token: null, error: null }));
        goto('/login');
    },
};
