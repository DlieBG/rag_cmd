class Command:
    def __init__(
        self,
        name: str,
        description: list[str],
        function: callable,
        arguments: dict[str, str],
    ):
        self.name = name
        self.description = description
        self.function = function
        self.arguments = arguments
