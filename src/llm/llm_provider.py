from db.db_provider import DBProvider
from models.chat import MessageModel
from core.agent import Agent

class LLMProvider:
    def __init__(self, db_provider: DBProvider, agent: Agent, id: str):
        self.db_provider = db_provider
        self.agent = agent
        self.id = id

    def send_message(self, text: str) -> list[MessageModel]:
        raise NotImplementedError()
