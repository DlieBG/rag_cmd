from models.chat import ChatIdModel, ChatModel, LLMType, MessageModel
from db.chat_model_provider import ChatModelProvider
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from typing import Optional
from bson import ObjectId
import os

MONGO_DATABASE_NAME = 'speak2neo'
MONGO_COLLECTION_NAME = 'chat_models'

class MongoChatModelProvider(ChatModelProvider):
    def __init__(self):
        self.client = MongoClient(
            os.getenv('MONGO_URI'),
            server_api=ServerApi('1'),
        )

        self.collection = self.client[MONGO_DATABASE_NAME][MONGO_COLLECTION_NAME]

    def _to_chat_model(self, chat_model: dict) -> Optional[ChatModel]:
        if not chat_model:
            return None

        return ChatModel(
            id=str(chat_model['_id']),
            llm_type=LLMType(chat_model['llm_type']),
            title=chat_model.get('title'),
            messages=[
                MessageModel.model_validate(message)
                    for message in chat_model['messages']
            ],
        )

    def get_chat_models(self) -> list[ChatModel]:
        return [
            self._to_chat_model(
                chat_model=chat_model,
            )
                for chat_model in self.collection.find(
                    filter={},
                )
        ]

    def get_chat_model(self, id: str) -> ChatModel:
        return self._to_chat_model(
            chat_model=self.collection.find_one(
                filter={
                    '_id': ObjectId(id),
                },
            ),
        )

    def create_chat_model(self, llm_type: LLMType) -> ChatIdModel:
        return ChatIdModel(
            id=str(
                self.collection.insert_one(
                    document=ChatModel(
                        llm_type=llm_type,
                    ).model_dump(
                        mode='json',
                        exclude={'id'},
                    ),
                ).inserted_id
            )
        )
    
    def update_chat_model(self, id: str, chat_model: ChatModel) -> None:
        self.collection.update_one(
            filter={
                '_id': ObjectId(id),
            },
            update={
                '$set': chat_model.model_dump(
                    mode='json',
                    exclude={'id', 'llm_type'},
                ),
            },
        )
