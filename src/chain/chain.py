from llm.llm_provider import LLMProvider
from rich import print
import json, re

class Chain:
    def __init__(self, llm_provider: LLMProvider):
        self.commands = {}
        self.llm_provider = llm_provider
        self.chat = llm_provider.start_chat()

    def command(self, name: str, description: str):
        """ Decorator to register a command function.
        """
        def decorator(command_function):
            self.commands[name] = {
                'description': description,
                'function': command_function,
                'arguments': {
                    argument: str(command_function.__annotations__[argument].__name__)
                        for argument in command_function.__annotations__
                },
            }

        return decorator

    def init(self, description: str):
        response = self.chat.send_message([
            'You are an intelligent AI assistant.',
            description,
            'You can answer questions provided by users.',
            'To get the necessary data to your context, you can execute commands.',
            'To execute a command, you have to send a JSON message with the following structure: {"command": "command_name", "arguments": {"argument_name": "argument_value"}}.',
            'You can execute multiple commands before you have to answer the user.',
            'To answer the user, you can use the command "answer" with the argument "message".',
            'The available commands are: [{}]'.format(', '.join([
                json.dumps({
                    'name': command,
                    'description': self.commands[command]['description'],
                    'arguments': self.commands[command]['arguments'],
                }) for command in self.commands
            ])),
            'To confirm that the instructions have been understood, reply with ok.',
        ])

        if response.strip() != 'ok':
            raise Exception('The instructions were not understood.')

    def ask(self, question: str) -> str:
        response = self.chat.send_message([
            f'The user asked: {question}',
        ])

        while True:
            requested_commands = re.findall(
                r'(?<=json\n){.*?}(?=\n)',
                response,
            )

            if len(requested_commands) != 1:
                raise Exception('Command execution not possible.')

            requested_command = json.loads(requested_commands[0])

            if requested_command['command'] == 'answer':
                return requested_command['arguments']['message']
            
            if requested_command['command'] not in self.commands:
                raise Exception('Command not found.')
            
            command = self.commands[requested_command['command']]
            print(f'Executing command: {requested_command}')

            command_answer = command['function'](
                **{
                    argument: requested_command['arguments'][argument]
                        for argument in command['arguments']
                },
            )
            # print(f'Providing answer: {command_answer}')

            response = self.chat.send_message([
                json.dumps(command_answer),
            ])
