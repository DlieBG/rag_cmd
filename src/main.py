from cache.mongo_provider import MongoCacheProvider
from llm.gemini_provider import GeminiLLMProvider
from adapter.test_adapter import TestAdapter
from adapter.neo4j_store import Neo4JStore
from chain.chain import Chain

cache = MongoCacheProvider()

chain = Chain(
    llm_provider=GeminiLLMProvider(),
    cache_provider=cache,
    debug=True,
)

test_adapter = TestAdapter(
    chain=chain,
)

neo4j_store = Neo4JStore(
    chain=chain,
)

chain.init(
    description=[
        'You have access to a medical graph database and you are an medical expert.',
    ],
)

print(
    chain.ask(
        question='How many patients are in remission?',
    )
    # chain.ask(
    #     question='Retrieve information about patients who did not achieve remission.',
    # )

    # chain.ask(
    #     question='Tell me the patient ids of patients treated with Olmkicept.',
    # )
    # chain.ask(
    #     question='Identify proteins in patients treated exclusively with Vedolizumab.',
    # )
)
