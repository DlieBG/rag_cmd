from src.models.chat import ChatIdModel, ChatModel, LLMType, MessageModel
from src.setup import db_provider, agent
from src.core.chat import Chat
from fastapi import FastAPI
import uvicorn

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

def start_api(reload: bool):
    uvicorn.run(
        app='src.api:api',
        host='0.0.0.0',
        port=8000,
        reload=reload,
    )
