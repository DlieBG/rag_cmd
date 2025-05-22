from src.adapter.agent_adapter import AgentAdapter
from src.models.schema_override import SchemaType
from dotenv import load_dotenv, find_dotenv
from src.core.agent import Agent
import json, os

load_dotenv(find_dotenv())

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

class SchemaOverrideAdapter(AgentAdapter):
    def __init__(self, agent: Agent, schema_type: SchemaType):
        if not schema_type == SchemaType.DEFAULT:
            @agent.command(            
                name='Neo4J Database Schema',
                description=[
                    'Get the schema of the Neo4J graph database.',
                    'You should always start with this command to understand the database.',
                ],
            )
            def database_schema():
                match schema_type:
                    case SchemaType.CLIQUE:
                        return self._clique_schema()
                    case SchemaType.HYPERGRAPH:
                        return self._hypergraph_schema()

    def _clique_schema(self) -> str:
        schema = {}

        return json.dumps(
            obj=schema,
            separators=(',', ':'),
        )

    def _hypergraph_schema(self) -> str:
        schema = {}

        return json.dumps(
            obj=schema,
            separators=(',', ':'),
        )
