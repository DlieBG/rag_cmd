class CacheProvider:
    def get_cached_command(self, key: dict) -> str:
        raise NotImplementedError()

    def set_cached_command(self, key: dict, result: str):
        raise NotImplementedError()
