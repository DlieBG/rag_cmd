from src.db.chat_model_provider import ChatModelProvider
from src.db.sample_provider import SampleProvider
from src.db.state_provider import StateProvider
from src.db.cache_provider import CacheProvider
from src.db.lock_provider import LockProvider

class DBProvider:
    def __init__(self, chat_model_provider: ChatModelProvider, lock_provider: LockProvider, state_provider: StateProvider, cache_provider: CacheProvider, sample_provider: SampleProvider):
        self.chat = chat_model_provider
        self.lock = lock_provider
        self.state = state_provider
        self.cache = cache_provider
        self.sample = sample_provider

    def remove_chat(self, id: str):
        self.chat.remove_chat_model(
            id=id,
        )
        self.state.remove_state(
            id=id,
        )
