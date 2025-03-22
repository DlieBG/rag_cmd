from llm.llm_provider import LLMChat, LLMProvider
from dotenv import load_dotenv, find_dotenv
from google import genai
from time import sleep
import os

load_dotenv(find_dotenv())

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class GeminiLLMChat(LLMChat):
    def __init__(self, chat: genai.chats.Chat):
        self.chat = chat
    
    def send_message(self, message: list[str], debug: bool = False) -> str:
        while True:
            try:
                response = self.chat.send_message(
                    message='\n'.join(message),
                )

                if debug:
                    print('Gemini usage metadata:', response.usage_metadata)

                return response.text
            except:
                print('Gemini Timeout, please wait...')
                sleep(30)

class GeminiLLMProvider(LLMProvider):
    def __init__(self):
        self.client = genai.Client(
            api_key=GEMINI_API_KEY,
        )
    
    def start_chat(self) -> GeminiLLMChat:
        return GeminiLLMChat(
            chat=self.client.chats.create(
                model='gemini-2.0-flash',
            ),
        )
