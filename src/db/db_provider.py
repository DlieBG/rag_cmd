from db.chat_model_provider import ChatModelProvider
from db.state_provider import StateProvider
from db.cache_provider import CacheProvider
from db.lock_provider import LockProvider

class DBProvider:
    def __init__(self, chat_model_provider: ChatModelProvider, lock_provider: LockProvider, state_provider: StateProvider, cache_provider: CacheProvider):
        self.chat = chat_model_provider
        self.lock = lock_provider
        self.state = state_provider
        self.cache = cache_provider
