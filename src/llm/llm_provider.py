class LLMChat:
    def send_message(self, message: list[str], debug: bool = False) -> str:
        raise NotImplementedError()

class LLMProvider:
    def start_chat(self) -> LLMChat:
        raise NotImplementedError()
