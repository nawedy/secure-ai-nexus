export type SecurityEventType =
  | 'authentication'
  | 'authorization'
  | 'data_access'
  | 'system_change'
  | 'api_access'
  | 'mfa'
  | 'user_management'
  | 'security_control'
  | 'compliance'
  | 'anomaly';

export type SecurityEventSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface SecurityEvent {
  id: string;
  type: SecurityEventType;
  subtype?: string;
  severity: SecurityEventSeverity;
  timestamp: string;
  userId?: string;
  sessionId?: string;
  source: string;
  details: string;
  metadata?: Record<string, any>;
  relatedEvents?: string[];
  ipAddress?: string;
  userAgent?: string;
  status: 'detected' | 'investigating' | 'resolved' | 'false_positive';
  resolution?: string;
}

export interface SecurityAlert {
  id: string;
  eventId: string;
  timestamp: string;
  severity: SecurityEventSeverity;
  status: 'new' | 'acknowledged' | 'investigating' | 'resolved';
  assignedTo?: string;
  description: string;
  actions: SecurityAlertAction[];
  metadata?: Record<string, any>;
}

export interface SecurityAlertAction {
  id: string;
  alertId: string;
  type: 'notification' | 'remediation' | 'investigation';
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  timestamp: string;
  details: string;
  performedBy?: string;
  result?: string;
}

export interface SecurityMetrics {
  eventCounts: Record<SecurityEventType, number>;
  severityCounts: Record<SecurityEventSeverity, number>;
  timeBasedMetrics: {
    hourly: number[];
    daily: number[];
    weekly: number[];
  };
  topSources: Array<{ source: string; count: number }>;
  responseMetrics: {
    averageResponseTime: number;
    resolutionRate: number;
    falsePositiveRate: number;
  };
} 