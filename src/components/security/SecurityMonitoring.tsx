import React, { useState } from 'react';
import { useSecurityMonitoring } from '@/hooks/useSecurityMonitoring';
import { SecurityEvent, SecurityEventSeverity } from '@/types/security';
import { SecurityMetricsChart } from './SecurityMetricsChart';
import { SecurityEventList } from './SecurityEventList';
import { SecurityAlertPanel } from './SecurityAlertPanel';

export const SecurityMonitoring: React.FC = () => {
  const {
    events,
    alerts,
    metrics,
    loading,
    error,
    acknowledgeAlert,
    resolveAlert,
  } = useSecurityMonitoring();

  const [selectedSeverity, setSelectedSeverity] = useState<SecurityEventSeverity[]>([]);
  const [timeRange, setTimeRange] = useState('24h');

  if (loading) return <div>Loading security monitoring...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">
          Security Monitoring
        </h2>
        <div className="flex space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="rounded-md border-gray-300"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          {/* Add more filters */}
        </div>
      </div>

      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <SecurityMetricsChart data={metrics} timeRange={timeRange} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Security Events
            </h3>
          </div>
          <SecurityEventList events={events} />
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">
              Active Alerts
            </h3>
          </div>
          <SecurityAlertPanel
            alerts={alerts}
            onAcknowledge={acknowledgeAlert}
            onResolve={resolveAlert}
          />
        </div>
      </div>
    </div>
  );
}; 