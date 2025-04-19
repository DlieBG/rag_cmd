class StateProvider:
    def get_state(self, id: str) -> list[dict]:
        raise NotImplementedError()

    def set_state(self, id: str, state: list[dict]):
        raise NotImplementedError()

    def remove_state(self, id: str):
        raise NotImplementedError()
