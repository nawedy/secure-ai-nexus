"""
Training Data Processor
Implements comprehensive data processing for ML model training
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from datetime import datetime
import logging

class DataProcessor:
    """
    Advanced data processor for ML training data preparation
    with comprehensive preprocessing capabilities
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()

        # Configure data processing
        self.sequence_length = config.get('sequence_length', 50)
        self.feature_dim = config.get('feature_dim', 64)
        self.validation_split = config.get('validation_split', 0.2)

    async def prepare_behavior_data(self) -> Dict[str, np.ndarray]:
        """Prepare data for behavior validation model"""
        try:
            self.logger.info("Preparing behavior validation data")

            # Load raw data
            raw_data = await self._load_behavior_data()

            # Extract features and labels
            features = await self._extract_behavior_features(raw_data)
            labels = await self._extract_behavior_labels(raw_data)

            # Preprocess features
            processed_features = await self._preprocess_behavior_features(features)

            # Encode labels
            encoded_labels = self.label_encoder.fit_transform(labels)

            return {
                'features': processed_features,
                'labels': encoded_labels,
                'feature_names': list(features.columns),
                'label_mapping': dict(zip(
                    self.label_encoder.classes_,
                    self.label_encoder.transform(self.label_encoder.classes_)
                ))
            }

        except Exception as e:
            self.logger.error(f"Error preparing behavior data: {str(e)}")
            raise

    async def prepare_coverage_data(self) -> Dict[str, np.ndarray]:
        """Prepare data for coverage analysis model"""
        try:
            self.logger.info("Preparing coverage analysis data")

            # Load raw data
            raw_data = await self._load_coverage_data()

            # Extract sequences and coverage information
            sequences = await self._extract_coverage_sequences(raw_data)
            coverage = await self._extract_coverage_metrics(raw_data)

            # Preprocess sequences
            processed_sequences = await self._preprocess_sequences(
                sequences,
                self.sequence_length
            )

            # Process coverage metrics
            processed_coverage = await self._process_coverage_metrics(coverage)

            return {
                'sequences': processed_sequences,
                'coverage': processed_coverage,
                'sequence_metadata': await self._generate_sequence_metadata(sequences)
            }

        except Exception as e:
            self.logger.error(f"Error preparing coverage data: {str(e)}")
            raise

    async def prepare_anomaly_data(self) -> Dict[str, np.ndarray]:
        """Prepare data for anomaly detection models"""
        try:
            self.logger.info("Preparing anomaly detection data")

            # Load raw data
            raw_data = await self._load_anomaly_data()

            # Extract normal and anomalous samples
            normal_samples = await self._extract_normal_samples(raw_data)
            anomalous_samples = await self._extract_anomalous_samples(raw_data)

            # Preprocess samples
            processed_normal = await self._preprocess_anomaly_samples(normal_samples)
            processed_anomalous = await self._preprocess_anomaly_samples(
                anomalous_samples
            )

            # Extract sequences
            sequences = await self._extract_anomaly_sequences(raw_data)
            processed_sequences = await self._preprocess_sequences(
                sequences,
                self.sequence_length
            )

            return {
                'normal_samples': processed_normal,
                'anomalous_samples': processed_anomalous,
                'sequences': processed_sequences,
                'metadata': {
                    'normal_distribution': await self._analyze_distribution(normal_samples),
                    'anomaly_distribution': await self._analyze_distribution(
                        anomalous_samples
                    )
                }
            }

        except Exception as e:
            self.logger.error(f"Error preparing anomaly data: {str(e)}")
            raise

    async def prepare_security_data(self) -> Dict[str, np.ndarray]:
        """Prepare data for security analysis models"""
        try:
            self.logger.info("Preparing security analysis data")

            # Load raw data
            raw_data = await self._load_security_data()

            # Prepare vulnerability data
            vulnerability_data = await self._prepare_vulnerability_data(raw_data)

            # Prepare pattern data
            pattern_data = await self._prepare_pattern_data(raw_data)

            return {
                'vulnerability_data': vulnerability_data,
                'pattern_data': pattern_data,
                'metadata': {
                    'vulnerability_stats': await self._calculate_vulnerability_stats(
                        vulnerability_data
                    ),
                    'pattern_stats': await self._calculate_pattern_stats(pattern_data)
                }
            }

        except Exception as e:
            self.logger.error(f"Error preparing security data: {str(e)}")
            raise

    async def _load_behavior_data(self) -> pd.DataFrame:
        """Load behavior validation data"""
        return pd.read_csv(self.config['behavior_data_path'])

    async def _load_coverage_data(self) -> pd.DataFrame:
        """Load coverage analysis data"""
        return pd.read_csv(self.config['coverage_data_path'])

    async def _load_anomaly_data(self) -> pd.DataFrame:
        """Load anomaly detection data"""
        return pd.read_csv(self.config['anomaly_data_path'])

    async def _load_security_data(self) -> pd.DataFrame:
        """Load security analysis data"""
        return pd.read_csv(self.config['security_data_path'])

    async def _extract_behavior_features(
        self,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """Extract features for behavior validation"""
        feature_columns = self.config['behavior_feature_columns']
        return data[feature_columns].copy()

    async def _extract_behavior_labels(
        self,
        data: pd.DataFrame
    ) -> np.ndarray:
        """Extract labels for behavior validation"""
        label_column = self.config['behavior_label_column']
        return data[label_column].values

    async def _preprocess_behavior_features(
        self,
        features: pd.DataFrame
    ) -> np.ndarray:
        """Preprocess behavior validation features"""
        # Handle missing values
        features = await self._handle_missing_values(features)

        # Scale features
        scaled_features = self.scaler.fit_transform(features)

        return scaled_features

    async def _extract_coverage_sequences(
        self,
        data: pd.DataFrame
    ) -> np.ndarray:
        """Extract sequences for coverage analysis"""
        sequence_columns = self.config['coverage_sequence_columns']
        return data[sequence_columns].values

    async def _extract_coverage_metrics(
        self,
        data: pd.DataFrame
    ) -> np.ndarray:
        """Extract coverage metrics"""
        metric_columns = self.config['coverage_metric_columns']
        return data[metric_columns].values

    async def _preprocess_sequences(
        self,
        sequences: np.ndarray,
        sequence_length: int
    ) -> np.ndarray:
        """Preprocess sequential data"""
        # Pad or truncate sequences
        processed_sequences = []
        for seq in sequences:
            if len(seq) > sequence_length:
                processed_sequences.append(seq[:sequence_length])
            else:
                padding = np.zeros((sequence_length - len(seq), seq.shape[1]))
                processed_sequences.append(np.vstack([seq, padding]))

        return np.array(processed_sequences)

    async def _extract_normal_samples(
        self,
        data: pd.DataFrame
    ) -> np.ndarray:
        """Extract normal samples for anomaly detection"""
        normal_mask = data[self.config['anomaly_label_column']] == 0
        return data[normal_mask][self.config['anomaly_feature_columns']].values

    async def _extract_anomalous_samples(
        self,
        data: pd.DataFrame
    ) -> np.ndarray:
        """Extract anomalous samples for anomaly detection"""
        anomaly_mask = data[self.config['anomaly_label_column']] == 1
        return data[anomaly_mask][self.config['anomaly_feature_columns']].values

    async def _prepare_vulnerability_data(
        self,
        data: pd.DataFrame
    ) -> Dict[str, np.ndarray]:
        """Prepare vulnerability detection data"""
        # Extract features and labels
        features = data[self.config['vulnerability_feature_columns']].values
        labels = data[self.config['vulnerability_label_column']].values

        # Preprocess features
        processed_features = self.scaler.fit_transform(features)

        return {
            'features': processed_features,
            'labels': labels
        }

    async def _prepare_pattern_data(
        self,
        data: pd.DataFrame
    ) -> Dict[str, np.ndarray]:
        """Prepare security pattern analysis data"""
        # Extract sequences and patterns
        sequences = await self._extract_security_sequences(data)
        patterns = await self._extract_security_patterns(data)

        # Preprocess data
        processed_sequences = await self._preprocess_sequences(
            sequences,
            self.sequence_length
        )

        return {
            'sequences': processed_sequences,
            'patterns': patterns
        }

    async def _handle_missing_values(
        self,
        data: pd.DataFrame
    ) -> pd.DataFrame:
        """Handle missing values in data"""
        # Fill numeric columns with mean
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        data[numeric_columns] = data[numeric_columns].fillna(data[numeric_columns].mean())

        # Fill categorical columns with mode
        categorical_columns = data.select_dtypes(include=['object']).columns
        data[categorical_columns] = data[categorical_columns].fillna(
            data[categorical_columns].mode().iloc[0]
        )

        return data

    async def _analyze_distribution(
        self,
        data: np.ndarray
    ) -> Dict[str, Any]:
        """Analyze data distribution"""
        return {
            'mean': np.mean(data, axis=0),
            'std': np.std(data, axis=0),
            'min': np.min(data, axis=0),
            'max': np.max(data, axis=0),
            'quartiles': np.percentile(data, [25, 50, 75], axis=0)
        }

    async def _generate_sequence_metadata(
        self,
        sequences: np.ndarray
    ) -> Dict[str, Any]:
        """Generate metadata for sequences"""
        return {
            'sequence_length': sequences.shape[1],
            'feature_dim': sequences.shape[2],
            'total_sequences': sequences.shape[0],
            'statistics': await self._analyze_distribution(sequences)
        }
