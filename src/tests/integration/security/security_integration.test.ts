import { describe, test, expect, beforeAll, afterAll } from 'vitest';
import { ThreatDetector } from '@/security/threat_detection';
import { AuditLogger } from '@/security/audit_logging';
import { ComplianceManager } from '@/compliance/compliance_manager';
import { SecurityMetrics } from '@/monitoring/security_metrics';

describe('Security System Integration', () => {
  let threatDetector: ThreatDetector;
  let auditLogger: AuditLogger;
  let complianceManager: ComplianceManager;
  let metrics: SecurityMetrics;

  beforeAll(async () => {
    // Initialize components
    threatDetector = new ThreatDetector();
    auditLogger = new AuditLogger();
    complianceManager = new ComplianceManager();
    metrics = new SecurityMetrics();
  });

  test('complete security workflow', async () => {
    // Simulate security event
    const securityEvent = {
      type: 'unauthorized_access',
      source: '192.168.1.100',
      timestamp: new Date(),
      details: {
        resource: 'api/sensitive',
        attempt: 'invalid_token'
      }
    };

    // Test threat detection
    const threatAnalysis = await threatDetector.analyzeEvent(securityEvent);
    expect(threatAnalysis.score).toBeGreaterThan(0.7);
    expect(threatAnalysis.details.riskLevel).toBe('high');

    // Test audit logging
    const logEntry = await auditLogger.logSecurityEvent(securityEvent);
    expect(logEntry.id).toBeDefined();
    expect(logEntry.verified).toBe(true);

    // Test compliance checks
    const complianceResult = await complianceManager.validateEvent(securityEvent);
    expect(complianceResult.compliant).toBe(false);
    expect(complianceResult.violations).toContain('access_control');

    // Verify metrics
    const securityMetrics = await metrics.getSecurityMetrics();
    expect(securityMetrics.threatDetections).toBeGreaterThan(0);
    expect(securityMetrics.complianceViolations).toBeGreaterThan(0);
  });

  test('threat response workflow', async () => {
    const threat = {
      type: 'brute_force',
      source: '10.0.0.5',
      attempts: 50,
      timeWindow: '5m'
    };

    // Test threat detection and response
    const response = await threatDetector.handleThreat(threat);
    expect(response.action).toBe('block_ip');
    expect(response.automated).toBe(true);

    // Verify audit trail
    const auditTrail = await auditLogger.getEventsByType('threat_response');
    expect(auditTrail).toContainEqual(expect.objectContaining({
      type: 'threat_response',
      action: 'block_ip'
    }));
  });

  test('compliance reporting workflow', async () => {
    // Test compliance report generation
    const report = await complianceManager.generateReport();
    expect(report.status).toBe('generated');
    expect(report.findings).toBeDefined();

    // Verify report storage
    const storedReport = await auditLogger.getComplianceReport(report.id);
    expect(storedReport).toEqual(report);

    // Check metrics update
    const updatedMetrics = await metrics.getComplianceMetrics();
    expect(updatedMetrics.reportsGenerated).toBeGreaterThan(0);
  });

  afterAll(async () => {
    // Cleanup test data
    await Promise.all([
      threatDetector.cleanup(),
      auditLogger.cleanup(),
      complianceManager.cleanup(),
      metrics.cleanup()
    ]);
  });
});
