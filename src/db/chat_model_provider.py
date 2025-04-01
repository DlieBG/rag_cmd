from src.models.chat import ChatIdModel, ChatModel, LLMType

class ChatModelProvider:
    def get_chat_models(self) -> list[ChatModel]:
        raise NotImplementedError()

    def get_chat_model(self, id: str) -> ChatModel:
        raise NotImplementedError()

    def create_chat_model(self, llm_type: LLMType) -> ChatIdModel:
        raise NotImplementedError()
    
    def update_chat_model(self, id: str, chat_model: ChatModel):
        raise NotImplementedError()
