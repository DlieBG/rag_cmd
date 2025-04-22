from src.adapter.agent_adapter import AgentAdapter
from src.db.db_provider import DBProvider
from src.core.agent import Agent

class Neo4JSampleAdapter(AgentAdapter):
    def __init__(self, agent: Agent, db_provider: DBProvider):
        @agent.command(
            name='Neo4J Cypher Query Examples',
            description=[
                'Get sample Cypher queries with a detailed description.',
                'You should always start with this command to understand how to use the database.',
            ],
        )
        def sample_queries():
            return db_provider.sample.get_samples()
