from llm.gemini_provider import GeminiLLMProvider
from models.chat import LLMType, MessageModel
from llm.llm_provider import LLMProvider
from db.db_provider import DBProvider
from core.agent import Agent

class Chat:
    def __init__(self, db_provider: DBProvider, agent: Agent, id: str):
        self.db_provider = db_provider
        self.agent = agent

        self.model = db_provider.chat.get_chat_model(
            id=id,
        )
        if not self.model:
            raise Exception('Chat not found.')

        self.llm_provider = self._get_llm_provider_class(
            llm_type=self.model.llm_type,
        )(
            db_provider=db_provider,
            agent=agent,
            id=id,
        )
    
    def _get_llm_provider_class(self, llm_type: LLMType) -> type[LLMProvider]:
        match llm_type:
            case LLMType.GEMINI:
                return GeminiLLMProvider
            case _:
                raise Exception('LLM type not supported.')

    def _aquire_lock(self):
        if not self.db_provider.lock.acquire(
            id=self.model.id,
        ):
            raise Exception('Chat is already locked.')
    
    def _release_lock(self):
        self.db_provider.lock.release(
            id=self.model.id,
        )

    def _refresh_model(self):
        self.model = self.db_provider.chat.get_chat_model(
            id=self.model.id,
        )
    
    def _update_model(self):
        self.db_provider.chat.update_chat_model(
            id=self.model.id,
            chat_model=self.model,
        )

    def send_message(self, text: str) -> list[MessageModel]:
        self._aquire_lock()

        try:
            self._refresh_model()

            response = self.llm_provider.send_message(
                text=text,
            )

            self.model.messages.extend(response)

            self._update_model()
        finally:
            self._release_lock()

        return response
