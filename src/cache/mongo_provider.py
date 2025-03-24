from cache.cache_provider import CacheProvider
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv, find_dotenv
from pymongo.server_api import ServerApi
import os

load_dotenv(find_dotenv())

MONGO_DATABASE_NAME = 'speak2neo'

class MongoCacheProvider(CacheProvider):
    def __init__(self):
        self.client = MongoClient(
            os.getenv('MONGO_URI'),
            server_api=ServerApi('1'),
        )

    def get(self, topic: str, key: str) -> dict:
        collection = self.client[MONGO_DATABASE_NAME][topic]

        cached = collection.find_one({
            'key': key,
        })

        if cached:
            return cached['value']
        
        return None
    
    def set(self, topic: str, key: str, value: dict):
        collection = self.client[MONGO_DATABASE_NAME][topic]

        collection.insert_one({
            'key': key,
            'value': repr(value),
        })
