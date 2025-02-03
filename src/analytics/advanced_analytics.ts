import { MetricsCollector } from '@/monitoring/metrics_collector';
import { SecurityEvent, ThreatLevel } from '@/types/security';
import { ML } from '@/lib/ml';
import { TimeSeriesAnalyzer } from '@/lib/analysis';

/**
 * Advanced Security Analytics System
 * Provides real-time analysis, pattern detection, and predictive alerts
 */
export class SecurityAnalytics {
  private metrics: MetricsCollector;
  private mlEngine: ML;
  private timeSeriesAnalyzer: TimeSeriesAnalyzer;
  private readonly PREDICTION_WINDOW = 3600; // 1 hour prediction window

  constructor() {
    this.metrics = new MetricsCollector();
    this.mlEngine = new ML({
      modelType: 'anomaly_detection',
      features: ['request_pattern', 'ip_behavior', 'payload_characteristics']
    });
    this.timeSeriesAnalyzer = new TimeSeriesAnalyzer();
  }

  /**
   * Analyze security events in real-time with ML-powered insights
   */
  async analyzeSecurityEvents(events: SecurityEvent[]): Promise<AnalysisResult> {
    const patterns = await this.detectPatterns(events);
    const anomalies = await this.detectAnomalies(events);
    const predictions = await this.generatePredictions(events);

    return {
      patterns,
      anomalies,
      predictions,
      riskScore: this.calculateRiskScore(patterns, anomalies, predictions)
    };
  }

  /**
   * Generate predictive alerts based on pattern analysis
   */
  async generatePredictiveAlerts(): Promise<PredictiveAlert[]> {
    const recentEvents = await this.metrics.getRecentEvents(this.PREDICTION_WINDOW);
    const predictions = await this.mlEngine.predict(recentEvents);

    return predictions.map(prediction => ({
      type: prediction.type,
      probability: prediction.confidence,
      estimatedTime: prediction.timestamp,
      severity: this.calculateSeverity(prediction),
      suggestedActions: this.generateActionPlan(prediction)
    }));
  }

  /**
   * Detect complex attack patterns using ML
   */
  private async detectPatterns(events: SecurityEvent[]): Promise<Pattern[]> {
    const timeSeriesData = this.timeSeriesAnalyzer.processEvents(events);
    const patterns = await this.mlEngine.detectPatterns(timeSeriesData);

    return patterns.map(pattern => ({
      type: pattern.type,
      confidence: pattern.score,
      relatedEvents: pattern.events,
      impact: this.assessImpact(pattern)
    }));
  }

  /**
   * Detect anomalies using advanced statistical analysis
   */
  private async detectAnomalies(events: SecurityEvent[]): Promise<Anomaly[]> {
    const baselineMetrics = await this.metrics.getBaseline();
    const currentMetrics = this.calculateMetrics(events);

    return this.mlEngine.detectAnomalies(currentMetrics, baselineMetrics);
  }

  /**
   * Generate future security predictions
   */
  private async generatePredictions(events: SecurityEvent[]): Promise<Prediction[]> {
    const historicalData = await this.metrics.getHistoricalData();
    const enrichedEvents = await this.enrichEventData(events);

    return this.mlEngine.generatePredictions(enrichedEvents, historicalData);
  }
}
