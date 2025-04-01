from src.db.lock_provider import LockProvider
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

MONGO_DATABASE_NAME = 'speak2neo'
MONGO_COLLECTION_NAME = 'locks'

class MongoLockProvider(LockProvider):
    def __init__(self):
        self.client = MongoClient(
            os.getenv('MONGO_URI'),
            server_api=ServerApi('1'),
        )

        self.collection = self.client[MONGO_DATABASE_NAME][MONGO_COLLECTION_NAME]

        self.collection.create_index(
            keys=[('chat_id', 1)],
            unique=True,
            expireAfterSeconds=300, # expire after 5 minutes
        )

    def acquire(self, id: str) -> bool:
        try:
            self.collection.insert_one(
                document={
                    'chat_id': id,
                },
            )

            return True
        except Exception:
            return False

    def release(self, id: str):
        self.collection.delete_one(
            filter={
                'chat_id': id,
            },
        )
