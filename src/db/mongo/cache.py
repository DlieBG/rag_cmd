from pymongo.mongo_client import MongoClient
from src.db.cache_provider import CacheProvider
from pymongo.server_api import ServerApi
import os

MONGO_DATABASE_NAME = 'speak2neo'
MONGO_COLLECTION_NAME = 'cache'

class MongoCacheProvider(CacheProvider):
    def __init__(self):
        self.client = MongoClient(
            os.getenv('MONGO_URI'),
            server_api=ServerApi('1'),
        )

        self.collection = self.client[MONGO_DATABASE_NAME][MONGO_COLLECTION_NAME]

        self.collection.create_index(
            keys=[('key', 1)],
            unique=True,
            expireAfterSeconds=86400, # expire after 1 day
        )

    def get_cached_command(self, key: dict) -> str:
        result = self.collection.find_one(
            filter={
                'key': key,
            },
        )

        if not result:
            return None

        return result['result']

    def set_cached_command(self, key: dict, result: str):
        self.collection.update_one(
            filter={
                'key': key,
            },
            update={
                '$set': {
                    'result': result,
                },
            },
            upsert=True,
        )
