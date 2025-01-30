import { User } from '@/types/auth';

interface SecurityEvent {
  type: string;
  details: string;
  userId?: string;
  timestamp?: string;
  metadata?: Record<string, any>;
}

export const logSecurityEvent = async (event: SecurityEvent) => {
  try {
    const response = await fetch('/api/security/log', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...event,
        timestamp: event.timestamp || new Date().toISOString(),
      }),
    });

    if (!response.ok) {
      throw new Error('Failed to log security event');
    }

    return await response.json();
  } catch (error) {
    console.error('Security event logging failed:', error);
    // Still return success to prevent blocking user flow
    return true;
  }
};

export const getSecurityEvents = async (
  userId: string,
  options: {
    startDate?: Date;
    endDate?: Date;
    type?: string[];
    limit?: number;
  } = {}
) => {
  try {
    const queryParams = new URLSearchParams({
      userId,
      ...(options.startDate && { startDate: options.startDate.toISOString() }),
      ...(options.endDate && { endDate: options.endDate.toISOString() }),
      ...(options.type && { type: options.type.join(',') }),
      ...(options.limit && { limit: options.limit.toString() }),
    });

    const response = await fetch(`/api/security/events?${queryParams}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch security events');
    }

    return await response.json();
  } catch (error) {
    console.error('Failed to fetch security events:', error);
    throw error;
  }
}; 