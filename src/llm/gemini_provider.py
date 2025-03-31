from models.chat import MessageModel, RoleType, CommandModel
from google.genai.chats import Chat, Part, Content
from google.genai.types import FunctionResponse
from dotenv import load_dotenv, find_dotenv
from llm.llm_provider import LLMProvider
from db.db_provider import DBProvider
from google.genai import types
from core.agent import Agent
from google import genai
import os

load_dotenv(find_dotenv())

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

class GeminiLLMProvider(LLMProvider):
    def __init__(self, db_provider: DBProvider, agent: Agent, id: str):
        super().__init__(
            db_provider=db_provider,
            agent=agent,
            id=id,
        )

        self.client = genai.Client(
            api_key=GEMINI_API_KEY,
        )

    def _to_gemini_data_type(self, data_type: str) -> str:
        match data_type:
            case 'str':
                return 'string'
            case 'int':
                return 'integer'

    def _send_gemini_message(self, chat: Chat, state: list[Content], text: str = None, function_responses: list[FunctionResponse] = None) -> Content:
        request_content = None

        if text:
            request_content = Content(
                role='user',
                parts=[
                    Part(
                        text=text,
                    ),
                ],
            )

        if function_responses:
            request_content = Content(
                role='user',
                parts=[
                    Part(
                        function_response=function_response,
                    )
                        for function_response in function_responses
                ],
            )

        if not request_content:
            raise Exception('Request content is empty.')

        response_content = chat.send_message(
            message=request_content.parts,
            config=types.GenerateContentConfig(
                temperature=1.3,
                system_instruction=self.agent.system_description,
                tools=[
                    types.Tool(
                        function_declarations=[
                            types.FunctionDeclaration(
                                name=command.name,
                                description=' '.join(command.description),
                                parameters={
                                    'type': 'object',
                                    'properties': {
                                        argument: {
                                            'type': self._to_gemini_data_type(
                                                data_type=command.arguments[argument],
                                            ),
                                        }
                                            for argument in command.arguments
                                    },
                                    'required': list(command.arguments.keys()),
                                } if len(command.arguments) > 0 else None,
                            )
                                for command in self.agent.commands
                        ]
                    )
                ],
                tool_config=types.ToolConfig(
                    function_calling_config=types.FunctionCallingConfig(
                        mode=types.FunctionCallingConfigMode.AUTO,
                    ),
                ),
            ),
        ).candidates[0].content

        state.append(request_content.model_dump(
            mode='json',
        ))
        state.append(response_content.model_dump(
            mode='json',
        ))

        return response_content

    def send_message(self, text: str) -> list[MessageModel]:
        messages: list[MessageModel] = [
            MessageModel(
                id='',
                role=RoleType.USER,
                text=text,
            ),
        ]

        state = self.db_provider.state.get_state(
            id=self.id,
        )

        chat = self.client.chats.create(
            model='gemini-2.0-flash',
            history=[
                Content.model_validate(content)
                    for content in state
            ],
        )

        response = self._send_gemini_message(
            chat=chat,
            state=state,
            text=text,
        )

        while True:
            function_responses = []

            for part in response.parts:
                if part.text:
                    messages.append(
                        MessageModel(
                            id='',
                            role=RoleType.ASSISTANT,
                            text=part.text,
                        )
                    )

                if part.function_call:
                    command_result, command_cache_hit = self.agent.execute_command(
                        command_name=part.function_call.name,
                        arguments=part.function_call.args,
                    )

                    messages.append(
                        MessageModel(
                            id='',
                            role=RoleType.ASSISTANT,
                            command=CommandModel(
                                name=part.function_call.name,
                                arguments=part.function_call.args,
                                result=command_result,
                                cache_hit=command_cache_hit,
                            ),
                        )
                    )

                    function_responses.append(
                        FunctionResponse(
                            name=part.function_call.name,
                            response={
                                'result': command_result,
                            },
                        )
                    )

            if len(function_responses) > 0:
                response = self._send_gemini_message(
                    chat=chat,
                    state=state,
                    function_responses=function_responses,
                )
            else:
                break

        self.db_provider.state.set_state(
            id=self.id,
            state=state,
        )

        return messages
