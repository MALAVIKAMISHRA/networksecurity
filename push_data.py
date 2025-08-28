import os
import sys
import json
import pymongo
import pandas as pd
from dotenv import load_dotenv
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

# Load environment variables from .env file
load_dotenv()

# FIX: Use the correct environment variable name to match your .env file
MONGO_URI = os.getenv("MONGO_DB_URL")
DATA_FILE_PATH = r"Network_Data\phisingData.csv"
DATABASE_NAME = "MALAVIKAAI"
COLLECTION_NAME = "NetworkData"


def push_data_to_db():
    """
    Reads data from a CSV file and pushes it to a MongoDB collection.
    """
    try:
        # 1. Read the data from the CSV file
        logging.info("Reading CSV file...")
        data = pd.read_csv(DATA_FILE_PATH)
        json_records = list(json.loads(data.to_json(orient="records")))
        logging.info(f"Successfully loaded {len(json_records)} records from CSV.")

        # 2. Connect to MongoDB
        logging.info("Connecting to MongoDB...")
        if not MONGO_URI:
            raise ValueError("MONGO_URI not found. Make sure it's set in your .env file.")
        
        mongo_client = pymongo.MongoClient(MONGO_URI)
        
        # 3. Insert the records into the collection
        logging.info(f"Inserting records into database '{DATABASE_NAME}' and collection '{COLLECTION_NAME}'...")
        db = mongo_client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # Optional: Delete existing data to avoid duplicates
        collection.delete_many({})
        
        collection.insert_many(json_records)
        logging.info(f"✅ Successfully inserted {len(json_records)} records into MongoDB.")

    except Exception as e:
        logging.error(e)
        raise NetworkSecurityException(e, sys) from e


if __name__ == '__main__':
    push_data_to_db()
