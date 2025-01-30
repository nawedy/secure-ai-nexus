import { useState, useEffect, useCallback } from 'react';
import { SecurityEvent, SecurityMetrics, SecurityAlert } from '@/types/security';
import { SecurityMonitor } from '@/services/monitoring/SecurityMonitor';

export const useSecurityMonitoring = () => {
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [metrics, setMetrics] = useState<SecurityMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const monitor = SecurityMonitor.getInstance();

  const fetchEvents = useCallback(async (params?: {
    startDate?: string;
    endDate?: string;
    types?: string[];
    severity?: string[];
    limit?: number;
  }) => {
    try {
      const queryParams = new URLSearchParams();
      if (params) {
        Object.entries(params).forEach(([key, value]) => {
          if (Array.isArray(value)) {
            value.forEach(v => queryParams.append(key, v));
          } else if (value) {
            queryParams.append(key, value);
          }
        });
      }

      const response = await fetch(`/api/security/events?${queryParams}`);
      if (!response.ok) throw new Error('Failed to fetch security events');
      
      const data = await response.json();
      setEvents(data.events);
    } catch (err) {
      setError(err as Error);
    }
  }, []);

  const fetchMetrics = useCallback(async () => {
    try {
      const response = await fetch('/api/security/metrics');
      if (!response.ok) throw new Error('Failed to fetch security metrics');
      
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      setError(err as Error);
    }
  }, []);

  const acknowledgeAlert = useCallback(async (alertId: string) => {
    try {
      const response = await fetch(`/api/security/alerts/${alertId}/acknowledge`, {
        method: 'POST',
      });
      
      if (!response.ok) throw new Error('Failed to acknowledge alert');
      
      setAlerts(current =>
        current.map(alert =>
          alert.id === alertId
            ? { ...alert, status: 'acknowledged' }
            : alert
        )
      );
    } catch (err) {
      setError(err as Error);
    }
  }, []);

  const resolveAlert = useCallback(async (
    alertId: string,
    resolution: string
  ) => {
    try {
      const response = await fetch(`/api/security/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ resolution }),
      });
      
      if (!response.ok) throw new Error('Failed to resolve alert');
      
      setAlerts(current =>
        current.map(alert =>
          alert.id === alertId
            ? { ...alert, status: 'resolved', resolution }
            : alert
        )
      );
    } catch (err) {
      setError(err as Error);
    }
  }, []);

  useEffect(() => {
    const initialize = async () => {
      try {
        await Promise.all([
          fetchEvents(),
          fetchMetrics(),
        ]);
      } finally {
        setLoading(false);
      }
    };

    initialize();

    const eventHandler = (event: SecurityEvent) => {
      setEvents(current => [event, ...current].slice(0, 1000));
    };

    monitor.on('newEvent', eventHandler);

    return () => {
      monitor.off('newEvent', eventHandler);
    };
  }, [fetchEvents, fetchMetrics]);

  return {
    events,
    alerts,
    metrics,
    loading,
    error,
    fetchEvents,
    fetchMetrics,
    acknowledgeAlert,
    resolveAlert,
  };
}; 