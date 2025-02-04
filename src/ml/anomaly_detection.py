"""
Advanced Anomaly Detection System
Implements sophisticated anomaly detection using ensemble ML models
"""

import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout

class AnomalyDetector:
    """
    Advanced anomaly detection system using ensemble of ML models
    """

    def __init__(self):
        self.isolation_forest = IsolationForest(
            n_estimators=200,
            contamination=0.1,
            max_samples='auto',
            random_state=42
        )

        self.scaler = StandardScaler()
        self.lstm_model = self._build_lstm_model()
        self.random_forest = RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            min_samples_split=2,
            random_state=42
        )

    def _build_lstm_model(self) -> Sequential:
        """Build LSTM model for sequence-based anomaly detection"""
        model = Sequential([
            LSTM(128, input_shape=(None, 50), return_sequences=True),
            Dropout(0.2),
            LSTM(64, return_sequences=False),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')
        ])

        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )

        return model

    async def detect_anomalies(
        self,
        data: np.ndarray,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect anomalies using ensemble approach
        """
        # Preprocess data
        scaled_data = self.scaler.fit_transform(data)

        # Get predictions from each model
        if_predictions = self.isolation_forest.fit_predict(scaled_data)
        rf_probas = self.random_forest.predict_proba(scaled_data)
        lstm_predictions = self.lstm_model.predict(
            scaled_data.reshape(-1, 1, scaled_data.shape[1])
        )

        # Combine predictions using weighted voting
        ensemble_predictions = self._combine_predictions(
            if_predictions,
            rf_probas,
            lstm_predictions,
            weights=[0.3, 0.3, 0.4]
        )

        # Analyze anomaly patterns
        patterns = self._analyze_anomaly_patterns(
            data,
            ensemble_predictions,
            context
        )

        return {
            'anomalies': ensemble_predictions,
            'patterns': patterns,
            'severity': self._calculate_severity(patterns),
            'recommendations': self._generate_recommendations(patterns)
        }

    def _combine_predictions(
        self,
        if_preds: np.ndarray,
        rf_probas: np.ndarray,
        lstm_preds: np.ndarray,
        weights: List[float]
    ) -> np.ndarray:
        """
        Combine predictions from multiple models using weighted voting
        """
        # Normalize isolation forest predictions
        if_normalized = np.where(if_preds == 1, 0, 1)

        # Combine predictions
        weighted_preds = (
            weights[0] * if_normalized +
            weights[1] * rf_probas[:, 1] +
            weights[2] * lstm_preds.flatten()
        )

        return weighted_preds > 0.5

    def _analyze_anomaly_patterns(
        self,
        data: np.ndarray,
        predictions: np.ndarray,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze patterns in detected anomalies
        """
        anomaly_indices = np.where(predictions)[0]

        if len(anomaly_indices) == 0:
            return {'patterns': [], 'clusters': [], 'temporal_analysis': {}}

        # Analyze temporal patterns
        temporal_patterns = self._analyze_temporal_patterns(
            data,
            anomaly_indices
        )

        # Cluster anomalies
        clusters = self._cluster_anomalies(
            data[anomaly_indices],
            context
        )

        # Analyze feature correlations
        correlations = self._analyze_feature_correlations(
            data,
            anomaly_indices
        )

        return {
            'patterns': temporal_patterns,
            'clusters': clusters,
            'correlations': correlations,
            'context_analysis': self._analyze_context(context) if context else None
        }

    def _analyze_temporal_patterns(
        self,
        data: np.ndarray,
        anomaly_indices: np.ndarray
    ) -> Dict[str, Any]:
        """
        Analyze temporal patterns in anomalies
        """
        # Calculate time differences between anomalies
        time_diffs = np.diff(anomaly_indices)

        return {
            'frequency': len(anomaly_indices) / len(data),
            'periodicity': self._detect_periodicity(time_diffs),
            'burst_patterns': self._detect_bursts(time_diffs),
            'trend': self._analyze_trend(data[anomaly_indices])
        }

    def _cluster_anomalies(
        self,
        anomaly_data: np.ndarray,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Cluster anomalies to identify patterns
        """
        from sklearn.cluster import DBSCAN

        # Cluster anomalies
        clustering = DBSCAN(eps=0.3, min_samples=2).fit(anomaly_data)

        return {
            'n_clusters': len(set(clustering.labels_)) - (1 if -1 in clustering.labels_ else 0),
            'cluster_sizes': np.bincount(clustering.labels_[clustering.labels_ >= 0]),
            'noise_points': np.sum(clustering.labels_ == -1),
            'cluster_analysis': self._analyze_clusters(anomaly_data, clustering.labels_)
        }

    def _calculate_severity(self, patterns: Dict[str, Any]) -> float:
        """
        Calculate severity score based on anomaly patterns
        """
        severity_factors = [
            patterns['patterns']['frequency'] * 0.3,
            len(patterns['clusters']['cluster_sizes']) * 0.2,
            np.mean(patterns['correlations'].values()) * 0.2,
            patterns['patterns']['trend']['slope'] * 0.3
        ]

        return np.mean(severity_factors)

    def _generate_recommendations(self, patterns: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on anomaly patterns
        """
        recommendations = []

        # Analyze frequency-based recommendations
        if patterns['patterns']['frequency'] > 0.1:
            recommendations.append(
                "High anomaly frequency detected. Consider adjusting monitoring thresholds."
            )

        # Analyze cluster-based recommendations
        if len(patterns['clusters']['cluster_sizes']) > 1:
            recommendations.append(
                "Multiple anomaly clusters detected. Investigate potential systemic issues."
            )

        # Analyze trend-based recommendations
        if patterns['patterns']['trend']['slope'] > 0:
            recommendations.append(
                "Increasing trend in anomalies detected. Implement preventive measures."
            )

        return recommendations
