class LockProvider:
    def acquire(self, id: str) -> bool:
        raise NotImplementedError()

    def release(self, id: str):
        raise NotImplementedError()
