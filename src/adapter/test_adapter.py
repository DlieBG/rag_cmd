from chain.chain import Chain

class TestAdapter:
    def __init__(self, chain: Chain):
        @chain.command(
            name='Neo4J Database Schema',
            description=[
                'Get the Schema Information of the Neo4J Database.',
                'FIRST OF ALL, YOU HAVE TO GET THE SCHEMA OF THE DATABASE. THEN YOU CAN QUERY THE DATABASE USING CYPHER QUERIES.',
            ],
        )
        def _():
            print('Neo4J Database Schema called')
            with open('test_schema.json', 'r') as file:
                return file.read()

        @chain.command(
            name='Neo4J Database Cypher Query',
            description=[
                'Query the Neo4J Database using Cypher Query.',
                'You have to align your capher queries to the schema of the database!',
            ],
        )
        def _(cypher: str):
            print('Neo4J Database Query', cypher)
            return 100
