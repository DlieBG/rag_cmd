from src.models.chat import RoleType, LLMType, MessageModel, ChatModel
from src.adapter.schema_override import SchemaOverrideAdapter
from src.models.sample import SampleCommandCreate
from src.models.schema import SchemaType
from src.models.scenario import Scenario
from src.setup import db_provider, agent
from rich.prompt import Confirm, Prompt
from rich.markdown import Markdown
from rich.console import Console
from src.core.chat import Chat
from src.api import start_api
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich import print
import click

@click.group()
def cli():
    pass

@cli.command(
    name='api',
    help='Start the API server.',
)
@click.option(
    '--reload',
    '-r',
    is_flag=True,
    help='Reload the server on code changes.',
)
def api(reload: bool):
    start_api(
        reload=reload,
    )

@cli.group(
    name='chats',
    help='Chat commands.'
)
def chats():
    pass

@chats.command(
    name='ls',
    help='List all chats.',
)
def list_chats():
    table = Table(
        title='Chats',
    )

    table.add_column(
        header='ID',
        justify='left',
    )
    table.add_column(
        header='Title',
        justify='left',
    )
    table.add_column(
        header='LLM Type',
        justify='left',
    )

    for chat_model in db_provider.chat.get_chat_models():
        table.add_row(
            chat_model.id,
            chat_model.title,
            chat_model.llm_type,
        )

    console = Console()
    console.print(table)

@chats.command(
    name='create',
    help='Create a new chat.',
)
@click.option(
    '--llm-type',
    '-l',
    type=click.Choice(
        choices=LLMType
    ),
    required=True,
    prompt=True,
    help='LLM type to use.',
)
def create_chat(llm_type: LLMType):
    print(
        db_provider.chat.create_chat_model(
            llm_type=llm_type,
        )
    )
    
def _render_message(message_model: MessageModel, console: Console):
    if message_model.role == RoleType.USER:
        console.print(
            Align.right(
                Panel(
                    Markdown(message_model.text, justify='right'),
                    title='[green]User',
                    title_align='right',
                    expand=False,
                ),
                width=100,
            )
        )

    if message_model.role == RoleType.ASSISTANT:
        if message_model.text:
            console.print(
                Align.left(
                    Panel(
                        Markdown(message_model.text),
                        title='[yellow]Assistant',
                        title_align='left',
                        expand=False,
                    ),
                    width=100,
                )
            )

        if message_model.command:
            from rich.pretty import Pretty
            console.print(
                Align.center(
                    Panel(
                        Pretty(
                            {
                                'command_name': message_model.command.name,
                                'arguments': message_model.command.arguments,
                                'cache_hit': message_model.command.cache_hit,
                            },
                            indent_size=4,
                            expand_all=True,
                        ),
                        title='[red]Command',
                        title_align='left',
                        expand=False,
                    ),
                )
            ) 

def _connect_to_chat(chat_model: ChatModel):
    console = Console()
    
    for message_model in chat_model.messages:
        _render_message(
            console=console,
            message_model=message_model,
        )

    while True:
        text = console.input(
            prompt='[blue]Enter Message: ',
        )

        messages = []

        with console.status('[magenta]Generating...'):
            messages = Chat(
                db_provider=db_provider,
                agent=agent,
                id=chat_model.id,
            ).send_message(
                text=text,
            )

        for message_model in messages:
            _render_message(
                console=console,
                message_model=message_model,
            )

@chats.command(
    name='connect',
    help='Connect to a chat.',
)
@click.option(
    '--id',
    '-i',
    type=str,
    required=True,
    prompt=True,
    help='ID of the chat to connect to.',
)
def connect_to_chat(id: str):
    chat_model = db_provider.chat.get_chat_model(
        id=id,
    )

    _connect_to_chat(
        chat_model=chat_model,
    )

@chats.command(
    name='debug',
    help='Create a new chat and connect to it.',
)
@click.option(
    '--llm-type',
    '-l',
    type=click.Choice(
        choices=LLMType
    ),
    required=True,
    prompt=True,
    help='LLM type to use.',
)
@click.option(
    '--rm',
    is_flag=True,
    default=False,
    show_default=True,
    help='Remove the chat after debugging.',
)
def debug_chat(llm_type: LLMType, rm: bool):
    chat_id = str(
        db_provider.chat.create_chat_model(
            llm_type=llm_type,
        ).id
    )

    print(chat_id)

    chat_model = db_provider.chat.get_chat_model(
        id=chat_id,
    )

    try:
        _connect_to_chat(
            chat_model=chat_model,
        )
    except KeyboardInterrupt:
        if rm:
            db_provider.remove_chat(
                id=chat_id,
            )

@chats.command(
    name='scenario',
    help='Create a new chat and replay a scenario file.',
)
@click.option(
    '--file',
    '-f',
    type=click.Path(
        exists=True,
        dir_okay=False,
        file_okay=True,
    ),
    required=True,
)
def scenario_chat(file: str):
    console = Console()

    with open(file, 'r') as f:
        scenario = Scenario.model_validate_json(
            json_data=f.read(),
        )

        if scenario.override_schema:
            if not scenario.override_schema_type:
                scenario.override_schema_type = Prompt.ask(
                    prompt='[magenta]How to override the schema?',
                    choices=SchemaType,
                    console=console,
                    default=SchemaType.DEFAULT,
                )

            SchemaOverrideAdapter(
                agent=agent,
                schema_type=scenario.override_schema_type,
            )

        chat_model = db_provider.chat.create_chat_model(
            llm_type=scenario.llm_type,
        )
        chat = Chat(
            db_provider=db_provider,
            agent=agent,
            id=chat_model.id,
        )

        for question in scenario.questions:
            messages = []

            with console.status('[magenta]Generating...'):
                messages = chat.send_message(
                    text=question,
                )

            for message_model in messages:
                _render_message(
                    console=console,
                    message_model=message_model,
                )

    if Confirm.ask(
        prompt='[magenta]Do you want to save the chat?',
        default=True,
        console=console,
    ):
        return console.print(
            f'[magenta]Chat saved with ID: [red]{chat_model.id}'
        )
        
    db_provider.remove_chat(
        id=chat_model.id,
    )

@cli.group(
    name='samples',
    help='Sample commands.'
)
def samples():
    pass

@samples.command(
    name='ls',
    help='List all samples.',
)
def list_samples():
    table = Table(
        title='Samples',
    )

    table.add_column(
        header='ID',
        justify='left',
    )
    table.add_column(
        header='Description',
        justify='left',
    )
    table.add_column(
        header='Tags',
        justify='left',
    )
    table.add_column(
        header='Cypher',
        justify='left',
    )

    for sample in db_provider.sample.get_samples():
        table.add_row(
            sample.id,
            sample.description,
            ', '.join(sample.tags),
            sample.cypher,
        )

    console = Console()
    console.print(table)

@samples.command(
    name='create',
    help='Create a new sample.',
)
@click.option(
    '--cypher',
    '-c',
    type=str,
    required=True,
    prompt='Cypher query',
    help='Cypher query to use.',
)
@click.option(
    '--tags',
    '-t',
    type=str,
    required=True,
    prompt='Tags (comma separated)',
    help='Tags to use.',
)
@click.option(
    '--description',
    '-d',
    type=str,
    required=True,
    prompt='Description',
    help='Description of the sample.',
)
def create_sample(cypher: str, tags: str, description: str):
    tags = [tag.strip() for tag in tags.split(',')]

    print(
        db_provider.sample.create_sample(
            sample=SampleCommandCreate(
                cypher=cypher,
                tags=tags,
                description=description,
            ),
        )
    )

@samples.command(
    name='rm',
    help='Remove a sample.',
)
@click.option(
    '--id',
    '-i',
    type=str,
    required=True,
    prompt='ID',
    help='ID of the sample to delete.',
)
def remove_sample(id: str):
    db_provider.sample.remove_sample(
        id=id,
    )

    print(f'Sample {id} deleted.')
