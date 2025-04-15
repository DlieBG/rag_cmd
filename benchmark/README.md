# Benchmark Suite

This directory contains scripts and utilities for benchmarking the RAG system's ability to generate Cypher queries from natural language questions based on different datasets.

## Files

*   `run_benchmark.py`: The main script to execute the benchmarks for SPCQL and CypherBench datasets. It initializes the RAG system, loads data, runs questions through the system, extracts generated Cypher, compares it against expected queries, and reports accuracy.
*   `extract_spcql_schema.py`: Contains logic to parse the SPCQL dataset files and generate an aggregated, inferred schema representation. This is used by `run_benchmark.py` for the SPCQL benchmark.
*   `cypherbench.py`: Defines the `CypherBenchLoader` class, responsible for fetching and processing data from the CypherBench dataset hosted on Hugging Face.
*   `spcql.py`: Defines the `SPCQLLoader` class, responsible for loading and processing data from the local SPCQL dataset files.

## Benchmarks

### 1. SPCQL (Schema-based QA)

*   **Data Retrieval:** The `SPCQLLoader` class (`spcql.py`) reads the SPCQL dataset files (e.g., `dev.json`, `test.json`) from the specified local path. Each entry typically contains a natural language question (`query`) and the corresponding gold standard Cypher query (`cypher`).
*   **System Connection:**
    *   Since the actual graph database for SPCQL is not available (available on BAIDU drive @ https://pan.baidu.com/s/1aqMZFMOOpiB1GWUo5-I7xQ?pwd=b6ix not accessible without a Chinese Phone Number), the benchmark simulates the interaction.
    *   An inferred schema is generated from the dataset itself using `aggregate_schema` (`extract_spcql_schema.py`).
    *   The `run_benchmark.py` script **monkey-patches** the agent's `neo4j_database_schema` command during the benchmark run. Instead of querying a live database for its schema, the command is temporarily replaced to return this pre-generated inferred schema.
    *   Other database interaction commands (`neo4j_database_cypher_query`, `neo4j_database_node_property_values`, `neo4j_database_sample_nodes`) are also monkey-patched to prevent actual database calls and return dummy data (e.g., empty lists), ensuring the benchmark tests the LLM's ability to generate queries based *only* on the provided schema and question, without relying on live data exploration.

### 2. CypherBench (NL-to-Cypher Translation)

*   **Data Retrieval:** The `CypherBenchLoader` class (`cypherbench.py`) fetches data splits (e.g., `train`, `test`, `validation`) directly from the `cypherbench/cypherbench` dataset on Hugging Face Hub. It retrieves rows containing natural language questions (`nl_question`) and gold standard Cypher queries (`gold_cypher`).
*   **System Connection:**
    *   The current implementation in `run_benchmark.py` for CypherBench focuses primarily on the direct translation task from natural language to Cypher.
    *   The prompt provided to the LLM (`Generate a Cypher query for the following question: {question}. Only return the Cypher query.`) does not explicitly include schema information derived from the CypherBench dataset context.
    *   Unlike the SPCQL benchmark, specific command patching for schema or data retrieval is *not* performed within the `run_benchmark_cypherbench` function itself. The test evaluates the LLM's ability to generate Cypher based mainly on the question, potentially leveraging its internal knowledge or patterns learned during training.

## Running the Benchmarks

Execute the main script from the project root directory:

```bash
python benchmark/run_benchmark.py
```
