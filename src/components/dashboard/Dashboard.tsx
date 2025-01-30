import React from 'react';
import { useMetrics } from '@/hooks/useMetrics';
import { MetricsChart } from './MetricsChart';
import { SecurityStatus } from './SecurityStatus';
import { RecentActivity } from './RecentActivity';

export const Dashboard: React.FC = () => {
  const { metrics, loading, error } = useMetrics();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error loading metrics</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">API Usage</h3>
          <MetricsChart data={metrics.apiUsage} />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">Model Performance</h3>
          <MetricsChart data={metrics.modelPerformance} />
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900">Security Status</h3>
          <SecurityStatus status={metrics.securityStatus} />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
        </div>
        <RecentActivity activities={metrics.recentActivity} />
      </div>
    </div>
  );
};

// Security Status Component
const SecurityStatus: React.FC<{ status: any }> = ({ status }) => {
  return (
    <div className="space-y-4">
      {Object.entries(status).map(([key, value]: [string, any]) => (
        <div key={key} className="flex justify-between items-center">
          <span className="text-sm text-gray-600">{key}</span>
          <span
            className={`px-2 py-1 rounded-full text-xs ${
              value.status === 'secure'
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {value.status}
          </span>
        </div>
      ))}
    </div>
  );
}; 