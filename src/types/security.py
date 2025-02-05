from dataclasses import dataclass
from typing import Literal, Optional, Any, Dict, List, Union


SecurityEventType = Literal[
    'authentication',
    'authorization',
    'data_access',
    'system_change',
    'api_access',
    'mfa',
    'user_management',
    'security_control',
    'compliance',
    'anomaly'
]

SecurityEventSeverity = Literal['low', 'medium', 'high', 'critical']


@dataclass
class SecurityEvent:
    id: str
    type: SecurityEventType
    subtype: Optional[str] = None
    severity: SecurityEventSeverity
    timestamp: str
    userId: Optional[str] = None
    sessionId: Optional[str] = None
    source: str
    details: str
    metadata: Optional[Dict[str, Any]] = None
    relatedEvents: Optional[List[str]] = None
    ipAddress: Optional[str] = None
    userAgent: Optional[str] = None
    status: Literal['detected', 'investigating', 'resolved', 'false_positive']
    resolution: Optional[str] = None


@dataclass
class SecurityAlert:
    id: str
    eventId: str
    timestamp: str
    severity: SecurityEventSeverity
    status: Literal['new', 'acknowledged', 'investigating', 'resolved']
    assignedTo: Optional[str] = None
    description: str
    actions: List['SecurityAlertAction']
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class SecurityAlertAction:
    id: str
    alertId: str
    type: Literal['notification', 'remediation', 'investigation']
    status: Literal['pending', 'in_progress', 'completed', 'failed']
    timestamp: str
    details: str
    performedBy: Optional[str] = None
    result: Optional[str] = None


@dataclass
class SecurityMetrics:
    eventCounts: Dict[SecurityEventType, int]
    severityCounts: Dict[SecurityEventSeverity, int]
    timeBasedMetrics: Dict[str, List[int]]
    topSources: List[Dict[str, Union[str, int]]]
    responseMetrics: Dict[str, Union[float, int]]