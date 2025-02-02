#!/usr/bin/env python3
import logging
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from typing import Dict, List
import json
from pathlib import Path
from datetime import datetime, timedelta
import pickle

logger = logging.getLogger(__name__)

class PredictiveAnalytics:
    """System behavior prediction and proactive maintenance"""

    def __init__(self):
        self.model_path = Path('models')
        self.model_path.mkdir(exist_ok=True)
        self.prediction_history = Path('prediction_history.json')
        self.training_data = Path('training_data.csv')
        self.models = {}

    async def train_models(self):
        """Train prediction models"""
        try:
            # Load historical data
            data = pd.read_csv(self.training_data)

            # Train resource usage model
            self.models['resource_usage'] = await self._train_resource_model(data)

            # Train performance model
            self.models['performance'] = await self._train_performance_model(data)

            # Train reliability model
            self.models['reliability'] = await self._train_reliability_model(data)

            await self._save_models()

        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            raise

    async def predict_issues(self) -> List[Dict]:
        """Predict potential future issues"""
        predictions = []

        try:
            # Predict resource usage
            resource_predictions = await self._predict_resource_usage()
            if resource_predictions['risk_level'] > 0.7:
                predictions.append(resource_predictions)

            # Predict performance issues
            perf_predictions = await self._predict_performance()
            if perf_predictions['risk_level'] > 0.7:
                predictions.append(perf_predictions)

            # Predict reliability issues
            rel_predictions = await self._predict_reliability()
            if rel_predictions['risk_level'] > 0.7:
                predictions.append(rel_predictions)

            await self._log_predictions(predictions)
            return predictions

        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise

    async def _train_resource_model(self, data: pd.DataFrame) -> RandomForestRegressor:
        """Train resource usage prediction model"""
        X = data[['cpu_usage', 'memory_usage', 'disk_usage', 'network_usage']]
        y = data['resource_warning']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        model = RandomForestRegressor(n_estimators=100)
        model.fit(X_train, y_train)

        return model

    async def _predict_resource_usage(self) -> Dict:
        """Predict future resource usage"""
        current_metrics = await self._get_current_metrics()
        prediction = self.models['resource_usage'].predict([current_metrics])[0]

        return {
            'type': 'resource_usage',
            'prediction': prediction,
            'risk_level': self._calculate_risk_level(prediction),
            'timeframe': '24h'
        }

    async def _train_performance_model(self, data: pd.DataFrame) -> RandomForestRegressor:
        """Train performance prediction model"""
        X = data[['response_time', 'error_rate', 'throughput']]
        y = data['performance_warning']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        model = RandomForestRegressor(n_estimators=100)
        model.fit(X_train, y_train)

        return model

    async def _train_reliability_model(self, data: pd.DataFrame) -> RandomForestRegressor:
        """Train reliability prediction model"""
        X = data[['error_rate', 'uptime', 'incident_count']]
        y = data['reliability_warning']

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

        model = RandomForestRegressor(n_estimators=100)
        model.fit(X_train, y_train)

        return model

    async def _save_models(self):
        """Save trained models"""
        for name, model in self.models.items():
            model_file = self.model_path / f"{name}_model.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump(model, f)
            logger.info(f"Model saved: {name}")

    def _calculate_risk_level(self, prediction: float) -> float:
        """Calculate risk level from prediction"""
        # Normalize prediction to 0-1 range
        return min(max(prediction / 100, 0), 1)

    async def _log_predictions(self, predictions: List[Dict]):
        """Log prediction results"""
        history = []
        if self.prediction_history.exists():
            history = json.loads(self.prediction_history.read_text())

        history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'predictions': predictions
        })

        self.prediction_history.write_text(json.dumps(history, indent=2))

if __name__ == "__main__":
    analytics = PredictiveAnalytics()
    asyncio.run(analytics.train_models())
