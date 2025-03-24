class CacheProvider:
    def get(self, topic: str, key: str) -> dict:
        raise NotImplementedError()

    def set(self, topic: str, key: str, value: dict):
        raise NotImplementedError()
