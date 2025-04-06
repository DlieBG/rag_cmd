from openai.types.chat import ChatCompletionMessage, ChatCompletionToolMessageParam
from src.llm.llm_provider import LLMProvider
from dotenv import load_dotenv, find_dotenv
from src.db.db_provider import DBProvider
from src.models.chat import MessageModel, RoleType, CommandModel
from src.core.agent import Agent
from openai import Client
import json, os

load_dotenv(find_dotenv())

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

class DeepseekLLMProvider(LLMProvider):
    def __init__(self, db_provider: DBProvider, agent: Agent, id: str):
        super().__init__(
            db_provider=db_provider,
            agent=agent,
            id=id,
        )

        self.client = Client(
            api_key=DEEPSEEK_API_KEY,
            base_url='https://api.deepseek.com/v1',
        )
    
    def _to_deepseek_data_type(self, data_type: str) -> str:
        match data_type:
            case 'str':
                return 'string'
            case 'int':
                return 'integer'

    def _send_deepseek_message(self, state: list[dict], text: str = None, function_responses: list[ChatCompletionToolMessageParam] = None) -> ChatCompletionMessage:
        request_contents = []

        if text:
            request_contents.append(
                {
                    'role': 'user',
                    'content': text,
                }
            )

        if function_responses:
            request_contents.extend(function_responses)

        response_content: ChatCompletionMessage = self.client.chat.completions.create(
            model='deepseek-chat',
            messages=[
                {
                    'role': 'system',
                    'content': ' '.join(self.agent.system_description),
                },
                *state,
                *request_contents,
            ],
            temperature=1.3,
            tools=[
                {
                    'type': 'function',
                    'function': {
                        'name': command.name,
                        'description': ' '.join(command.description),
                        'parameters': {
                            'type': 'object',
                            'properties': {
                                argument: {
                                    'type': self._to_deepseek_data_type(
                                        data_type=command.arguments[argument],
                                    ),
                                } 
                                    for argument in command.arguments
                            },
                            'required': list(command.arguments.keys()),
                        },
                    },
                }
                    for command in self.agent.commands
            ],
            stream=False,
        ).choices[0].message

        state.extend(request_contents)
        state.append(
            response_content.model_dump(
                mode='json',
            )
        )

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

        response = self._send_deepseek_message(
            state=state,
            text=text,
        )

        while True:
            function_responses = []

            if response.content:
                messages.append(
                    MessageModel(
                        id='',
                        role=response.role,
                        text=response.content,
                    )
                )

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    command_arguments = json.loads(
                        s=tool_call.function.arguments,
                    )

                    command_result, command_cache_hit = self.agent.execute_command(
                        command_name=tool_call.function.name,
                        arguments=command_arguments,
                    )

                    messages.append(
                        MessageModel(
                            id='',
                            role=RoleType.ASSISTANT,
                            command=CommandModel(
                                name=tool_call.function.name,
                                arguments=command_arguments,
                                result=command_result,
                                cache_hit=command_cache_hit,
                            ),
                        )
                    )

                    function_responses.append(
                        ChatCompletionToolMessageParam(
                            role='tool',
                            tool_call_id=tool_call.id,
                            content=command_result,
                        )
                    )

            if len(function_responses) > 0:
                response = self._send_deepseek_message(
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
