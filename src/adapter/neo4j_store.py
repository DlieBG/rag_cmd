from adapter.agent_adapter import AgentAdapter
from dotenv import load_dotenv, find_dotenv
from neo4j import GraphDatabase
from core.agent import Agent
import json, os

load_dotenv(find_dotenv())

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

class Neo4JStoreAdapter(AgentAdapter):
    def __init__(self, agent: Agent):
        @agent.command(
            name='Neo4J Database Schema',
            description=[
                'Get the Schema Information of the Neo4J Database.',
                'FIRST OF ALL, YOU HAVE TO GET THE SCHEMA OF THE DATABASE. THEN YOU CAN QUERY THE DATABASE USING CYPHER QUERIES.',
            ],
        )
        def database_schema():
            with GraphDatabase.driver(
                uri=NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
            ) as driver:
                records, _, _ = driver.execute_query(
                    'CALL apoc.meta.schema();'
                )

                schema = records[0]['value']

                for object in schema:
                    for property in schema[object]['properties']:
                        # reduce properties to their type
                        schema[object]['properties'][property] = schema[object]['properties'][property]['type']

                    for relationship in list(
                        schema[object].get('relationships', [])
                    ):
                        # reduce redundant relationship properties
                        del schema[object]['relationships'][relationship]['properties']

                        if schema[object]['relationships'][relationship]['count'] == 0:
                            # remove relationships with no nodes
                            del schema[object]['relationships'][relationship]
        
                return json.dumps(
                    obj=schema,
                    separators=(',', ':'),
                )
        
        @agent.command(
            name='Neo4J Database Node Property Values',
            description=[
                'Get the possible VALUES of a nodes property.',
                'YOU SHOULD ALWAYS QUERY THE POSSIBLE STRING VALUES FOR YOUR QUERIES!',
            ],
        )
        def node_property_values(node_name: str, property_name: str):
            with GraphDatabase.driver(
                uri=NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
            ) as driver:
                records, _, _ = driver.execute_query(
                    f'MATCH (n:{node_name}) RETURN DISTINCT n.{property_name} AS value;'
                )

                return [
                    r['value'] for r in records
                ]
        
        @agent.command(
            name='Neo4J Database Sample Nodes',
            description=[
                'Get some sample Nodes.',
                'IT IS VERY HELPFUL TO SEE SOME SAMPLE ENTRIES OF THE DATABASE BEFORE WRITING YOUR QUERIES!',
            ],
        )
        def sample_nodes(node_name: str, count: int):
            with GraphDatabase.driver(
                uri=NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
            ) as driver:
                records, _, _ = driver.execute_query(
                    f'MATCH (n:{node_name}) RETURN n LIMIT {count};'
                )

                return records

        @agent.command(
            name='Neo4J Database Cypher Query',
            description=[
                'Query the Neo4J Database using Cypher Query.',
                'You have to align your capher queries to the schema of the database!',
                'Most of the time you should run multiple queries to get the desired information.',
            ],
        )
        def cypher_query(cypher: str):
            with GraphDatabase.driver(
                uri=NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
            ) as driver:
                try:
                    records, _, _ = driver.execute_query(
                        cypher
                    )

                    return records
                except Exception as e:
                    return str(e)
