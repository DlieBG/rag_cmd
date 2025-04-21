from src.models.sample import SampleCommand, SampleCommandCreate, SampleCommandId
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

@api.delete(
    path='/chat/{id}',
    tags=['Chat'],
    status_code=204,
)
def remove_chat(id: str):
    db_provider.remove_chat(
        id=id,
    )

@api.get(
    path='/sample',
    tags=['Sample'],
)
def get_samples() -> list[SampleCommand]:
    return db_provider.sample.get_samples()

@api.get(
    path='/sample/{id}',
    tags=['Sample'],
)
def get_sample(id: str) -> SampleCommand:
    return db_provider.sample.get_sample(
        id=id,
    )

@api.post(
    path='/sample',
    tags=['Sample'],
    status_code=201,
)
def create_sample(sample: SampleCommandCreate) -> SampleCommandId:
    return db_provider.sample.create_sample(
        sample=sample,
    )

@api.put(
    path='/sample/{id}',
    tags=['Sample'],
    status_code=204,
)
def update_sample(id: str, sample: SampleCommandCreate):
    return db_provider.sample.update_sample(
        id=id,
        sample=sample,
    )

@api.delete(
    path='/sample/{id}',
    tags=['Sample'],
    status_code=204,
)
def remove_sample(id: str):
    db_provider.sample.remove_sample(
        id=id,
    )

def start_api(reload: bool):
    uvicorn.run(
        app='src.api:api',
        host='0.0.0.0',
        port=8000,
        reload=reload,
    )
