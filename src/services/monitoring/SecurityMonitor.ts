import { SecurityEvent, SecurityEventType, SecurityEventSeverity } from '@/types/security';
import { EventEmitter } from 'events';

export class SecurityMonitor extends EventEmitter {
  private static instance: SecurityMonitor;
  private eventBuffer: SecurityEvent[] = [];
  private readonly bufferSize = 1000;
  private readonly flushInterval = 5000; // 5 seconds

  private constructor() {
    super();
    this.initializeFlushInterval();
  }

  public static getInstance(): SecurityMonitor {
    if (!SecurityMonitor.instance) {
      SecurityMonitor.instance = new SecurityMonitor();
    }
    return SecurityMonitor.instance;
  }

  private initializeFlushInterval(): void {
    setInterval(() => {
      this.flushEvents();
    }, this.flushInterval);
  }

  public async logEvent(event: Omit<SecurityEvent, 'id' | 'timestamp'>): Promise<void> {
    const fullEvent: SecurityEvent = {
      id: this.generateEventId(),
      timestamp: new Date().toISOString(),
      ...event,
    };

    this.eventBuffer.push(fullEvent);
    this.emit('newEvent', fullEvent);

    if (this.shouldTriggerAlert(fullEvent)) {
      await this.triggerAlert(fullEvent);
    }

    if (this.eventBuffer.length >= this.bufferSize) {
      await this.flushEvents();
    }
  }

  private async flushEvents(): Promise<void> {
    if (this.eventBuffer.length === 0) return;

    try {
      await fetch('/api/security/events/batch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          events: this.eventBuffer,
        }),
      });

      this.eventBuffer = [];
    } catch (error) {
      console.error('Failed to flush security events:', error);
      // Implement retry mechanism
    }
  }

  private generateEventId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private shouldTriggerAlert(event: SecurityEvent): boolean {
    return (
      event.severity === 'critical' ||
      event.severity === 'high' ||
      this.isAnomalousEvent(event)
    );
  }

  private isAnomalousEvent(event: SecurityEvent): boolean {
    // Implement anomaly detection logic
    return false;
  }

  private async triggerAlert(event: SecurityEvent): Promise<void> {
    try {
      await fetch('/api/security/alerts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event,
          alertType: 'security_violation',
          priority: event.severity,
        }),
      });
    } catch (error) {
      console.error('Failed to trigger security alert:', error);
    }
  }
} 