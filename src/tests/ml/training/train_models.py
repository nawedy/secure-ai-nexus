"""
ML Model Training Pipeline Runner
Executes training for all ML components
"""

import asyncio
import argparse
import yaml
import logging
from datetime import datetime
from typing import Dict, Any
from model_trainer import ModelTrainer
from data_processor import DataProcessor

async def load_config(config_path: str) -> Dict[str, Any]:
    """Load training configuration"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

async def setup_logging(config: Dict[str, Any]) -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=config.get('log_level', 'INFO'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
            logging.StreamHandler()
        ]
    )

async def train_models(config: Dict[str, Any]) -> None:
    """Train all ML models"""
    logger = logging.getLogger(__name__)
    logger.info("Starting model training pipeline")

    try:
        # Initialize trainer and data processor
        trainer = ModelTrainer(config)
        data_processor = DataProcessor(config)

        # Train behavior validator
        logger.info("Training behavior validator")
        behavior_data = await data_processor.prepare_behavior_data()
        behavior_model = await trainer.train_behavior_validator(behavior_data)
        logger.info("Behavior validator training completed")

        # Train coverage analyzer
        logger.info("Training coverage analyzer")
        coverage_data = await data_processor.prepare_coverage_data()
        coverage_model = await trainer.train_coverage_analyzer(coverage_data)
        logger.info("Coverage analyzer training completed")

        # Train anomaly detection models
        logger.info("Training anomaly detection models")
        anomaly_data = await data_processor.prepare_anomaly_data()
        autoencoder, sequence_model = await trainer.train_anomaly_detector(anomaly_data)
        logger.info("Anomaly detection models training completed")

        # Train security models
        logger.info("Training security models")
        security_data = await data_processor.prepare_security_data()
        vulnerability_detector, pattern_analyzer = await trainer.train_security_models(security_data)
        logger.info("Security models training completed")

        logger.info("All models trained successfully")

    except Exception as e:
        logger.error(f"Error during model training: {str(e)}")
        raise

async def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Train ML models for testing components')
    parser.add_argument('--config', type=str, required=True, help='Path to configuration file')
    args = parser.parse_args()

    # Load configuration
    config = await load_config(args.config)

    # Setup logging
    await setup_logging(config)

    # Train models
    await train_models(config)

if __name__ == '__main__':
    asyncio.run(main())
