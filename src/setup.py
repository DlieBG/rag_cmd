from src.db.mongo.chat_model import MongoChatModelProvider
from src.adapter.neo4j_store import Neo4JStoreAdapter
from src.db.mongo.state import MongoStateProvider
from src.db.mongo.cache import MongoCacheProvider
from src.db.mongo.lock import MongoLockProvider
from src.db.db_provider import DBProvider
from src.core.agent import Agent

db_provider = DBProvider(
    chat_model_provider=MongoChatModelProvider(),
    lock_provider=MongoLockProvider(),
    state_provider=MongoStateProvider(),
    cache_provider=MongoCacheProvider(),
)

agent = Agent(
    system_description='You have access to a medical graph database and you are an medical expert. Please query the property values before writing cypher queries. You should always start with the Schema Query.',
    db_provider=db_provider,
    cache_commands=True,
)

Neo4JStoreAdapter(
    agent=agent,
)
