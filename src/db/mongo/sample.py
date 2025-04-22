from src.models.sample import SampleCommand, SampleCommandCreate, SampleCommandId
from src.db.sample_provider import SampleProvider
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import Optional
from bson import ObjectId
import os

MONGO_DATABASE_NAME = 'speak2neo'
MONGO_COLLECTION_NAME = 'samples'

class MongoSampleProvider(SampleProvider):
    def __init__(self):
        self.client = MongoClient(
            os.getenv('MONGO_URI'),
            server_api=ServerApi('1'),
            connect=False,
        )

        self.collection = self.client[MONGO_DATABASE_NAME][MONGO_COLLECTION_NAME]

    def _to_sample(self, sample: dict) -> Optional[SampleCommand]:
        if not sample:
            return None
        
        return SampleCommand(
            id=str(sample['_id']),
            cypher=sample['cypher'],
            tags=sample['tags'],
            description=sample['description'],
        )

    def get_samples(self) -> list[SampleCommand]:
        return [
            self._to_sample(
                sample=sample,
            )
                for sample in self.collection.find(
                    filter={},
                )
        ]

    def get_sample(self, id):
        return self._to_sample(
            sample=self.collection.find_one(
                filter={
                    '_id': ObjectId(id),
                },
            ),
        )

    def create_sample(self, sample: SampleCommandCreate) -> SampleCommandId:
        return SampleCommandId(
            id=str(
                self.collection.insert_one(
                    document=sample.model_dump(
                        mode='json',
                    ),
                ).inserted_id,
            ),
        )

    def update_sample(self, id: str, sample: SampleCommandCreate):
        self.collection.update_one(
            filter={
                '_id': ObjectId(id),
            },
            update={
                '$set': sample.model_dump(
                    mode='json',
                ),
            },
        )

    def remove_sample(self, id: str):
        self.collection.delete_one(
            filter={
                '_id': ObjectId(id),
            },
        )
