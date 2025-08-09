import os
import sys
import json
import pymongo
import certifi
import pandas as pd
from dotenv import load_dotenv
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

# Load environment variables
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class NetworkDataExtract:
    def __init__(self):
        # [CORRECTION] Removed empty try-except block as it was redundant.
        self.mongo_client = None

    def csv_to_json_convertor(self, file_path):
        try:
            data = pd.read_csv(file_path)
            # No need for .reset_index() if the CSV has a standard 0-based index
            records = list(json.loads(data.to_json(orient="records")))
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records, database, collection):
        try:
            # [CORRECTION] Simplified the client connection.
            # Modern pymongo handles TLS/SSL certificates automatically in most environments.
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            
            db = self.mongo_client[database]
            col = db[collection]

            col.insert_many(records)
            return len(records)
        except Exception as e:
            raise NetworkSecurityException(e, sys)


if __name__ == '__main__':
    try:
        FILE_PATH = r"Network_Data\phisingData.csv"
        DATABASE = "MALAVIKAAI"
        COLLECTION = "NetworkData"

        networkobj = NetworkDataExtract()

        records = networkobj.csv_to_json_convertor(file_path=FILE_PATH)
        logging.info(f"✅ Loaded {len(records)} records from CSV.")

        # Show first 3 records for verification
        print("\nSample records from CSV:")
        for rec in records[:3]:
            print(rec)

        no_of_records = networkobj.insert_data_mongodb(records, DATABASE, COLLECTION)
        logging.info(f"✅ Successfully inserted {no_of_records} records into MongoDB Atlas.")

    except Exception as e:
        # It's better to log the exception before raising your custom one
        logging.error(e)
        raise NetworkSecurityException(e, sys)
