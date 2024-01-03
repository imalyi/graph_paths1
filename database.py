import re
from pymongo import MongoClient, UpdateOne
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError
from bson import ObjectId


import logging


MONGO_CONNECT = "mongodb://gmaps:gmaps@bed:28017/"
MONGO_DB_NAME = "15min_new"
MONGO_DB_HOST = 123


class MongoDatabase:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.__connect()
        self.bulk_delete_points_of_interest()

    def __connect(self):
        try:
            self.client = MongoClient(MONGO_CONNECT, serverSelectionTimeoutMS=2000)
            self.db = self.client.get_database(MONGO_DB_NAME)
        except ServerSelectionTimeoutError:
            self.logger.error("Failed to connect to MongoDB server")

    def insert_many(self, data: dict):
        list_data = []
        for address, document in data.items():
            list_data.append(document.copy())
        self.db['address'].insert_many(list_data)

    def bulk_delete_points_of_interest(self):
        try:
            result = self.db['address'].delete_many({})
            deleted_count = result.deleted_count
            self.logger.info(f"Points of interest bulk deleted: {deleted_count} deleted")
        except Exception as e:
            self.logger.error(f"Error bulk deleting points of interest: {str(e)}")
