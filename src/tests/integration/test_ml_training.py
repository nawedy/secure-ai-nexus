"""
Integration Tests for ML Training Pipeline
Implements comprehensive testing of the ML model training components
"""

import pytest
import numpy as np
import pandas as pd
import tensorflow as tf
from pathlib import Path
import yaml
import asyncio
from datetime import datetime
from typing import Dict, Any, Generator

from ml.training.model_trainer import ModelTrainer
from ml.training.data_processor import DataProcessor

class TestMLTrainingPipeline:
    """Integration tests for ML training pipeline"""

    @pytest.fixture(autouse=True)
    async def setup(self) -> Generator:
        """Setup test environment"""
        # Load test configuration
        config_path = Path("src/tests/ml/training/config.yaml")
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Modify config for testing
        self.config["epochs"] = 2  # Reduce epochs for testing
        self.config["batch_size"] = 16
        self.config["experiment_name"] = "test_ml_training"

        # Create test data directories
        test_data_dir = Path("test_data")
        test_data_dir.mkdir(exist_ok=True)

        # Initialize components
        self.trainer = ModelTrainer(self.config)
        self.data_processor = DataProcessor(self.config)

        # Generate test data
        await self._generate_test_data()

        yield

        # Cleanup
        await self._cleanup_test_data()

    async def test_behavior_validator_training(self) -> None:
        """Test behavior validator model training"""
        # Prepare test data
        behavior_data = await self.data_processor.prepare_behavior_data()

        # Validate data structure
        assert "features" in behavior_data
        assert "labels" in behavior_data
        assert behavior_data["features"].shape[1] == self.config["input_dim"]

        # Train model
        model = await self.trainer.train_behavior_validator(behavior_data)

        # Validate model
        assert isinstance(model, tf.keras.Model)
        assert len(model.layers) > 0

        # Test predictions
        test_input = np.random.random((1, self.config["input_dim"]))
        predictions = model.predict(test_input)
        assert predictions.shape == (1, 1)
        assert 0 <= predictions[0, 0] <= 1

    async def test_coverage_analyzer_training(self) -> None:
        """Test coverage analyzer model training"""
        # Prepare test data
        coverage_data = await self.data_processor.prepare_coverage_data()

        # Validate data structure
        assert "sequences" in coverage_data
        assert "coverage" in coverage_data
        assert coverage_data["sequences"].shape[2] == self.config["feature_dim"]

        # Train model
        model = await self.trainer.train_coverage_analyzer(coverage_data)

        # Validate model
        assert isinstance(model, tf.keras.Model)
        assert len(model.layers) > 0

        # Test predictions
        test_input = np.random.random((1, self.config["sequence_length"], self.config["feature_dim"]))
        predictions = model.predict(test_input)
        assert predictions.shape == (1, self.config["coverage_dim"])
        assert np.all((predictions >= 0) & (predictions <= 1))

    async def test_anomaly_detector_training(self) -> None:
        """Test anomaly detection models training"""
        # Prepare test data
        anomaly_data = await self.data_processor.prepare_anomaly_data()

        # Validate data structure
        assert "normal_samples" in anomaly_data
        assert "sequences" in anomaly_data

        # Train models
        autoencoder, sequence_model = await self.trainer.train_anomaly_detector(anomaly_data)

        # Validate autoencoder
        assert isinstance(autoencoder, tf.keras.Model)
        test_input = np.random.random((1, anomaly_data["normal_samples"].shape[1]))
        reconstructions = autoencoder.predict(test_input)
        assert reconstructions.shape == test_input.shape

        # Validate sequence model
        assert isinstance(sequence_model, tf.keras.Model)
        test_sequence = np.random.random((1, self.config["sequence_length"], anomaly_data["sequences"].shape[2]))
        sequence_predictions = sequence_model.predict(test_sequence)
        assert sequence_predictions.shape == (1, anomaly_data["sequences"].shape[2])

    async def test_security_models_training(self) -> None:
        """Test security analysis models training"""
        # Prepare test data
        security_data = await self.data_processor.prepare_security_data()

        # Validate data structure
        assert "vulnerability_data" in security_data
        assert "pattern_data" in security_data

        # Train models
        vulnerability_detector, pattern_analyzer = await self.trainer.train_security_models(security_data)

        # Validate vulnerability detector
        assert isinstance(vulnerability_detector, tf.keras.Model)
        test_input = np.random.random((1, security_data["vulnerability_data"]["features"].shape[1]))
        vuln_predictions = vulnerability_detector.predict(test_input)
        assert vuln_predictions.shape == (1, 1)
        assert 0 <= vuln_predictions[0, 0] <= 1

        # Validate pattern analyzer
        assert isinstance(pattern_analyzer, tf.keras.Model)
        test_sequence = np.random.random((1, self.config["sequence_length"], security_data["pattern_data"]["sequences"].shape[2]))
        pattern_predictions = pattern_analyzer.predict(test_sequence)
        assert pattern_predictions.shape[1] == security_data["pattern_data"]["patterns"].shape[1]

    async def test_end_to_end_training_pipeline(self) -> None:
        """Test complete training pipeline execution"""
        # Test data preparation
        behavior_data = await self.data_processor.prepare_behavior_data()
        coverage_data = await self.data_processor.prepare_coverage_data()
        anomaly_data = await self.data_processor.prepare_anomaly_data()
        security_data = await self.data_processor.prepare_security_data()

        # Train all models
        behavior_model = await self.trainer.train_behavior_validator(behavior_data)
        coverage_model = await self.trainer.train_coverage_analyzer(coverage_data)
        autoencoder, sequence_model = await self.trainer.train_anomaly_detector(anomaly_data)
        vulnerability_detector, pattern_analyzer = await self.trainer.train_security_models(security_data)

        # Validate training history
        assert len(self.trainer.training_history) > 0
        for model_name, history in self.trainer.training_history.items():
            assert "loss" in history
            assert "val_loss" in history
            assert len(history["loss"]) == self.config["epochs"]

    async def test_model_persistence(self) -> None:
        """Test model saving and loading"""
        # Train a model
        behavior_data = await self.data_processor.prepare_behavior_data()
        model = await self.trainer.train_behavior_validator(behavior_data)

        # Save model
        save_path = Path("test_data/test_model.h5")
        model.save(save_path)

        # Load model
        loaded_model = tf.keras.models.load_model(save_path)

        # Compare predictions
        test_input = np.random.random((1, self.config["input_dim"]))
        original_predictions = model.predict(test_input)
        loaded_predictions = loaded_model.predict(test_input)
        np.testing.assert_array_almost_equal(original_predictions, loaded_predictions)

    async def test_data_processor_robustness(self) -> None:
        """Test data processor robustness"""
        # Test missing value handling
        test_data = pd.DataFrame({
            "feature1": [1.0, np.nan, 3.0],
            "feature2": [np.nan, 2.0, 3.0],
            "category": ["A", None, "B"]
        })

        processed_data = await self.data_processor._handle_missing_values(test_data)
        assert not processed_data.isnull().any().any()

        # Test sequence padding
        short_sequence = np.random.random((10, 5))
        padded_sequence = await self.data_processor._preprocess_sequences(
            np.array([short_sequence]),
            sequence_length=20
        )
        assert padded_sequence.shape == (1, 20, 5)

    async def _generate_test_data(self) -> None:
        """Generate test data for training"""
        num_samples = 100

        # Generate behavior data
        behavior_data = pd.DataFrame(
            np.random.random((num_samples, len(self.config["behavior_feature_columns"]))),
            columns=self.config["behavior_feature_columns"]
        )
        behavior_data[self.config["behavior_label_column"]] = np.random.randint(2, size=num_samples)
        behavior_data.to_csv("test_data/behavior_validation.csv", index=False)

        # Update config paths
        self.config.update({
            "behavior_data_path": "test_data/behavior_validation.csv",
            "coverage_data_path": "test_data/coverage_analysis.csv",
            "anomaly_data_path": "test_data/anomaly_detection.csv",
            "security_data_path": "test_data/security_analysis.csv"
        })

    async def _cleanup_test_data(self) -> None:
        """Clean up test data and artifacts"""
        import shutil

        # Remove test data directory
        shutil.rmtree("test_data", ignore_errors=True)

        # Remove model checkpoints
        shutil.rmtree("checkpoints", ignore_errors=True)

        # Remove logs
        shutil.rmtree("logs", ignore_errors=True)
