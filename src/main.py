from src.api import start_api
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
