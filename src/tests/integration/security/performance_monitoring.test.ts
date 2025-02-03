import { describe, test, expect, beforeAll } from 'vitest';
import { SecurityPerformanceMonitor } from '@/monitoring/security_performance';
import { ThreatDetector } from '@/security/threat_detection';
import { AuditLogger } from '@/security/audit_logging';

describe('Security Performance Monitoring', () => {
  let performanceMonitor: SecurityPerformanceMonitor;
  let threatDetector: ThreatDetector;
  let auditLogger: AuditLogger;

  beforeAll(async () => {
    performanceMonitor = new SecurityPerformanceMonitor();
    threatDetector = new ThreatDetector();
    auditLogger = new AuditLogger();
  });

  test('monitor threat detection performance', async () => {
    const startMetrics = await performanceMonitor.getCurrentMetrics();

    // Generate load
    const events = Array.from({ length: 100 }, (_, i) => ({
      type: 'suspicious_activity',
      timestamp: new Date(),
      id: `event-${i}`
    }));

    const startTime = Date.now();
    await Promise.all(events.map(event => threatDetector.analyzeEvent(event)));
    const duration = Date.now() - startTime;

    const endMetrics = await performanceMonitor.getCurrentMetrics();

    // Verify performance metrics
    expect(duration).toBeLessThan(5000); // Should process 100 events in < 5s
    expect(endMetrics.avgProcessingTime).toBeLessThan(50); // < 50ms per event
    expect(endMetrics.memoryUsage).toBeLessThan(512 * 1024 * 1024); // < 512MB
  });

  test('monitor audit logging performance', async () => {
    const metrics = await performanceMonitor.startMonitoring('audit_logging');

    // Generate audit logs
    const logs = Array.from({ length: 1000 }, (_, i) => ({
      type: 'security_audit',
      timestamp: new Date(),
      details: `Test log ${i}`
    }));

    await Promise.all(logs.map(log => auditLogger.log(log)));

    const performanceData = await performanceMonitor.stopMonitoring('audit_logging');

    // Verify performance
    expect(performanceData.throughput).toBeGreaterThan(500); // >500 logs/sec
    expect(performanceData.latency.p95).toBeLessThan(100); // p95 < 100ms
    expect(performanceData.errors).toBe(0);
  });
});
