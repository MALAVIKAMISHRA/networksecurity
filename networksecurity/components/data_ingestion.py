from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
import os
import sys
import numpy as np
import pandas as pd
import pymongo
from sklearn.model_selection import train_test_split

# REMOVED: The os.getenv call from the global scope.

class DataIngestion:
    # FIX: The MongoDB URL is now passed directly into the constructor.
    def __init__(self, data_ingestion_config: DataIngestionConfig, mongo_db_url: str):
        try:
            self.data_ingestion_config = data_ingestion_config
            
            if not mongo_db_url:
                raise ValueError("MongoDB URL was not provided to the DataIngestion class.")
            
            self.mongo_client = pymongo.MongoClient(mongo_db_url)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def export_collection_as_dataframe(self):
        """Reads data from MongoDB and returns it as a pandas DataFrame."""
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            
            logging.info(f"Reading data from db: '{database_name}', collection: '{collection_name}'")
            collection = self.mongo_client[database_name][collection_name]
            df = pd.DataFrame(list(collection.find()))
            logging.info(f"Found {len(df)} records.")

            if "_id" in df.columns:
                df = df.drop(columns=["_id"], axis=1)

            df.replace({"na": np.nan}, inplace=True)
            return df
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def export_data_into_feature_store(self, dataframe: pd.DataFrame):
        """Saves the DataFrame to the feature store file path."""
        try:
            logging.info("Saving data to feature store.")
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            logging.info(f"Data saved to: {feature_store_file_path}")
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        """Splits the DataFrame and saves train and test sets."""
        try:
            logging.info("Performing train-test split.")
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio, random_state=42
            )
            logging.info(f"Train set shape: {train_set.shape}, Test set shape: {test_set.shape}")

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)

            logging.info("Exporting train and test files.")
            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )
            logging.info(f"Train file saved to: {self.data_ingestion_config.training_file_path}")
            logging.info(f"Test file saved to: {self.data_ingestion_config.testing_file_path}")
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        """Main method to orchestrate the data ingestion process."""
        try:
            logging.info(">>> Starting Data Ingestion pipeline <<<")
            dataframe = self.export_collection_as_dataframe()
            
            self.export_data_into_feature_store(dataframe)
            
            self.split_data_as_train_test(dataframe)
            logging.info(">>> Data Ingestion pipeline complete <<<")

            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
