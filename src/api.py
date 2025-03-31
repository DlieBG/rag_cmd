from models.chat import ChatIdModel, ChatModel, LLMType, MessageModel
from fastapi import FastAPI
from setup import db_provider, agent
from core.chat import Chat

api = FastAPI()

@api.get(
    path='/chat',
    tags=['Chat'],
)
def get_chats() -> list[ChatModel]:
    return db_provider.chat.get_chat_models()

@api.get(
    path='/chat/{id}',
    tags=['Chat'],
)
def get_chat(id: str) -> ChatModel:
    return db_provider.chat.get_chat_model(
        id=id,
    )

@api.post(
    path='/chat',
    tags=['Chat'],
    status_code=201,
)
def create_chat(llm_type: LLMType) -> ChatIdModel:
    return db_provider.chat.create_chat_model(
        llm_type=llm_type,
    )

@api.put(
    path='/chat/{id}/message',
    tags=['Chat'],
)
def send_message(id: str, text: str) -> list[MessageModel]:
    chat = Chat(
        db_provider=db_provider,
        agent=agent,
        id=id,
    )

    return chat.send_message(
        text=text,
    )
