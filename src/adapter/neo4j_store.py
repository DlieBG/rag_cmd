from adapter.chain_adapter import ChainAdapter
from dotenv import load_dotenv, find_dotenv
from neo4j import GraphDatabase
from chain.chain import Chain
import os

load_dotenv(find_dotenv())

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USER = os.getenv('NEO4J_USER')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')

class Neo4JStore(ChainAdapter):
    def __init__(self, chain: Chain):
        @chain.command(
            name='Neo4J Database Schema',
            description=[
                'Get the Schema Information of the Neo4J Database.',
                'FIRST OF ALL, YOU HAVE TO GET THE SCHEMA OF THE DATABASE. THEN YOU CAN QUERY THE DATABASE USING CYPHER QUERIES.',
            ],
        )
        def _():
            with GraphDatabase.driver(
                uri=NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
            ) as driver:
                records, _, _ = driver.execute_query(
                    'CALL apoc.meta.schema();'
                )

                return records[0]['value']
        
        @chain.command(
            name='Neo4J Node Property String Values',
            description=[
                'Get the possible STRING VALUES of a nodes property.',
                'YOU SHOULD ALWAYS QUERY THE POSSIBLE STRING VALUES FOR YOUR QUERIES!',
            ],
        )
        def _(node_name: str, property_name: str):
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

        @chain.command(
            name='Neo4J Database Cypher Query',
            description=[
                'Query the Neo4J Database using Cypher Query.',
                'You have to align your capher queries to the schema of the database!',
                'Most of the time you should run multiple queries to get the desired information.',
            ],
        )
        def _(cypher: str):
            with GraphDatabase.driver(
                uri=NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
            ) as driver:
                records, _, _ = driver.execute_query(
                    cypher
                )

                return records
