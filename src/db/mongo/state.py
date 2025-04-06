from src.db.state_provider import StateProvider
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
import os

MONGO_DATABASE_NAME = 'speak2neo'
MONGO_COLLECTION_NAME = 'state'

class MongoStateProvider(StateProvider):
    def __init__(self):
        self.client = MongoClient(
            os.getenv('MONGO_URI'),
            server_api=ServerApi('1'),
            connect=False,
        )

        self.collection = self.client[MONGO_DATABASE_NAME][MONGO_COLLECTION_NAME]

    def get_state(self, id: str) -> list[dict]:
        state = self.collection.find_one(
            filter={
                '_id': ObjectId(id),
            },
        )

        if not state:
            return []
        
        return state['state']

    def set_state(self, id: str, state: list[dict]):
        self.collection.update_one(
            filter={
                '_id': ObjectId(id),
            },
            update={
                '$set': {
                    'state': state,
                },
            },
            upsert=True,
        )

    def remove_state(self, id: str):
        self.collection.delete_one(
            filter={
                '_id': ObjectId(id),
            },
        )
