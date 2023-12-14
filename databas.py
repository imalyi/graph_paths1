import re
from pymongo import MongoClient, UpdateOne
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
from bson import ObjectId


import logging

logger = logging.getLogger(f"{__name__}_Database")

MONGO_CONNECT = "mongodb://gmaps:gmaps@bed:28017/"
MONGO_DB_NAME = "15min"
MONGO_DB_HOST = 123


class MongoDatabase:
    def __init__(self):
        self.__connect()

    def __connect(self):
        try:
            self.client = MongoClient(MONGO_CONNECT, serverSelectionTimeoutMS=2000)
            self.db = self.client.get_database(MONGO_DB_NAME)
        except ServerSelectionTimeoutError:
            logger.error("Failed to connect to MongoDB server")

    def insert_many(self, data: dict):
        list_data = []
        for address, document in data.items():
            list_data.append(document.copy())
        self.db['address'].insert_many(list_data)

    def bulk_delete_points_of_interest(self):
        try:
            result = self.db['address'].delete_many({})
            deleted_count = result.deleted_count
            logger.info(f"Points of interest bulk deleted: {deleted_count} deleted")

        except Exception as e:
            # Handle error
            logger.error(f"Error bulk deleting points of interest: {str(e)}")
