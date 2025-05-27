from src.db.db_provider import DBProvider
from src.core.command import Command

class Agent:
    """ Agent class to collect and execute commands for a specific agent use case.
    """
    def __init__(self, system_description: list[str], db_provider: DBProvider, cache_commands: bool = True):
        self.system_description = system_description
        self.db_provider = db_provider
        self.cache_commands = cache_commands

        self.commands: list[Command] = []
        self.omit_cache_commands: list[str] = []

    def command(self, name: str, description: list[str], omit_cache: bool = False) -> callable:
        """ Decorator to register a command function.
        """
        def decorator(command_function: callable):
            for command in self.commands:
                if command.name == name.replace(' ', '_').lower():
                    self.commands.remove(command)

            self.commands.append(
                Command(
                    name=name.replace(' ', '_').lower(),
                    description=description,
                    function=command_function,
                    arguments={
                        argument: str(command_function.__annotations__[argument].__name__)
                            for argument in command_function.__annotations__
                    },
                )
            )

            if omit_cache:
                self.omit_cache_commands.append(
                    name.replace(' ', '_').lower()
                )

        return decorator

    def execute_command(self, command_name: str, arguments: dict) -> tuple[str, bool]:
        """ Execute a registered command.
        """
        if self.cache_commands:
            if command_name not in self.omit_cache_commands:
                if (result := self.db_provider.cache.get_cached_command(
                    key={
                        'command_name': command_name,
                        'arguments': arguments,
                    },
                )):
                    return result, True

        for command in self.commands:
            if command.name == command_name:
                result = repr(
                    command.function(**arguments)
                )

                if self.cache_commands:
                    if command_name not in self.omit_cache_commands:
                        self.db_provider.cache.set_cached_command(
                            key={
                                'command_name': command_name,
                                'arguments': arguments,
                            },
                            result=result,
                        )

                return result, False

        raise Exception('Command not found.')
