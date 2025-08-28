import os
import sys
from dotenv import load_dotenv
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig
)
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

# FIX: Load environment variables at the very beginning of the script
load_dotenv()

if __name__ == "__main__":
    try:
        # 1. Read the MongoDB URL from the environment
        mongo_db_url = os.getenv("MONGO_DB_URL")
        if not mongo_db_url:
            raise ValueError("MONGO_DB_URL is not set in the .env file.")

        # 2. Setup Configuration
        training_pipeline_config = TrainingPipelineConfig()
        
        # --- Data Ingestion ---
        logging.info("Initiate the data ingestion")
        data_ingestion_config = DataIngestionConfig(training_pipeline_config=training_pipeline_config)
        data_ingestion = DataIngestion(
            data_ingestion_config=data_ingestion_config,
            mongo_db_url=mongo_db_url  # Pass the URL here
        )
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data Ingestion Completed")
        print(data_ingestion_artifact)

        # --- Data Validation ---
        logging.info("Initiate the data validation")
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data Validation Completed")
        print(data_validation_artifact)

        # --- Data Transformation ---
        logging.info("Data transformation started")
        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        data_transformation = DataTransformation(data_validation_artifact, data_transformation_config)
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logging.info("Data transformation completed")
        print(data_transformation_artifact)

        # --- Model Training ---
        logging.info("Model Training started")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config)
        model_trainer = ModelTrainer(
            model_trainer_config=model_trainer_config,
            data_transformation_artifact=data_transformation_artifact
        )
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logging.info("Model Training completed")
        print(model_trainer_artifact)

    except Exception as e:
        logging.error(e)
        raise NetworkSecurityException(e, sys) from e


