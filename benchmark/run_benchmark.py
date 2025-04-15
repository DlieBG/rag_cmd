import sys
import os
import uuid
import re
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from spcql import SPCQLLoader
from benchmark.extract_spcql_schema import aggregate_schema
from cypherbench import CypherBenchLoader


from src.setup import agent, db_provider
from src.core.chat import Chat
from src.core.agent import Agent
from src.db.db_provider import DBProvider
from src.models.chat import LLMType, RoleType, CommandModel, MessageModel

from rich.console import Console
from rich.table import Table

console = Console()

def initialize_rag_system():
    console.print("[info]Using pre-initialized agent and db_provider from src.setup")
    return agent, db_provider

def extract_cypher_query(messages: list[MessageModel]) -> str | None:
    for message in reversed(messages):
        if message.role == RoleType.ASSISTANT and message.command:
            if message.command.name == 'neo4j_database_cypher_query':
                return message.command.arguments.get('cypher')
    
    for message in reversed(messages):
        if message.role == RoleType.ASSISTANT and message.text:
            text = message.text.lower()
            
            import re
            cypher_block = re.search(r'```(?:cypher)?\s*(match|merge|create|call|with|return).*?```', 
                                    message.text, re.IGNORECASE | re.DOTALL)
            if cypher_block:
                query = cypher_block.group(0).strip('`').strip()
                if query.lower().startswith('cypher'):
                    query = query[6:].strip()
                return query
            
            if any(keyword in text for keyword in ['match ', 'merge ', 'create ', 'return ', 'where ']):
                lines = [line.strip() for line in message.text.split('\n') 
                        if any(keyword in line.lower() for keyword in 
                              ['match ', 'merge ', 'create ', 'return ', 'where '])]
                if lines:
                    return ' '.join(lines)
    
    return None

def run_benchmark_spcql(agent_instance: Agent, db_provider_instance: DBProvider, dataset_name: str = "dev"):
    """Runs the benchmark against a specified SPCQL dataset."""
    
    console.print("[info] Generating inferred schema from SPCQL dataset...")
    loader = SPCQLLoader()
    inferred_schema_data = aggregate_schema(loader)
    inferred_schema_json_string = json.dumps(inferred_schema_data, separators=(',', ':'))
    console.print("[info] Inferred schema generated.")
    
    loader = SPCQLLoader()
    if dataset_name not in loader.available_sets():
        console.print(f"[bold red]Error: Dataset '{dataset_name}' not available.[/]")
        console.print(f"Available sets: {loader.available_sets()}")
        return

    data = loader.get_data(dataset_name)
    console.print(f"\n[bold cyan]Running benchmark on '{dataset_name}' set ({len(data)} examples)...[/]")

    results = []
    correct_matches = 0
    query_found_count = 0

    llm_to_test = LLMType.GEMINI
    chat_id_model = db_provider_instance.chat.create_chat_model(llm_type=llm_to_test)
    chat_id = chat_id_model.id
    console.print(f"[info]Created temporary chat ID for benchmark: {chat_id} using {llm_to_test}")

    chat_instance = Chat(
        db_provider=db_provider_instance,
        agent=agent_instance,
        id=chat_id,
    )
    
    # --- Monkey-Patch the 'neo4j_database_schema' command ---
    original_schema_func = None
    schema_command_found = False
    
    console.print("[bold blue]DEBUG: Checking registered commands before patching...[/]")
    if not agent_instance.commands:
        console.print("[bold yellow]DEBUG: agent_instance.commands list is EMPTY![/]")
    else:
        console.print(f"[blue]DEBUG: Found {len(agent_instance.commands)} commands:[/]")
        for idx, cmd in enumerate(agent_instance.commands):
            console.print(f"[blue]DEBUG {idx}: Name={repr(cmd.name)}, Function={cmd.function}[/]")
    console.print("[bold blue]DEBUG: End of registered commands check.[/]")

    for command in agent_instance.commands:
        if command.name == 'neo4j_database_schema':
            console.print(f"[info] Found command '{command.name}', replacing its function.")
            original_schema_func = command.function
            schema_command_found = True
            break

    if not schema_command_found:
        console.print("[bold red]Error: Could not find 'neo4j_database_schema' command to monkey-patch.[/]")
        return # Cannot proceed without patching
    
    # --- Monkey-Patch the 'neo4j_database_cypher_query' command ---
    original_cypher_func = None
    cypher_command_found = False
    for command in agent_instance.commands:
        if command.name == 'neo4j_database_cypher_query':
            console.print(f"[info] Found command '{command.name}', replacing its function to prevent execution.")
            original_cypher_func = command.function

            # Define the replacement function
            def cypher_override_func(cypher: str):
                console.print(f"[DEBUG] Monkey-patched cypher function called with query: {cypher}. Preventing execution.")
                return []

            command.function = cypher_override_func
            cypher_command_found = True
            break

    if not cypher_command_found:
        console.print("[bold yellow]Warning: Could not find 'neo4j_database_cypher_query' command to monkey-patch. Execution might still be attempted.[/]")
    
    # --- Monkey-Patch 'neo4j_database_node_property_values' ---
    original_prop_values_func = None
    prop_values_command_found = False
    for command in agent_instance.commands:
        if command.name == 'neo4j_database_node_property_values':
            console.print(f"[info] Found command '{command.name}', replacing its function.")
            original_prop_values_func = command.function
            def prop_values_override_func(node_name: str, property_name: str):
                console.print(f"[DEBUG] Monkey-patched prop_values called for {node_name}.{property_name}. Returning empty list.")
                return [] # Return dummy empty list
            command.function = prop_values_override_func
            prop_values_command_found = True
            break
    if not prop_values_command_found:
        console.print("[bold yellow]Warning: Could not find 'neo4j_database_node_property_values' command to patch.[/]")
        
    # --- Monkey-Patch 'neo4j_database_sample_nodes' ---
    original_sample_nodes_func = None
    sample_nodes_command_found = False
    for command in agent_instance.commands:
        if command.name == 'neo4j_database_sample_nodes':
            console.print(f"[info] Found command '{command.name}', replacing its function.")
            original_sample_nodes_func = command.function
            def sample_nodes_override_func(node_name: str, count: int):
                console.print(f"[DEBUG] Monkey-patched sample_nodes called for {node_name}. Returning empty list.")
                return [] # Return dummy empty list
            command.function = sample_nodes_override_func
            sample_nodes_command_found = True
            break
    if not sample_nodes_command_found:
        console.print("[bold yellow]Warning: Could not find 'neo4j_database_sample_nodes' command to patch.[/]")
    

    for i, item in enumerate(data):
        question = item.get('query')
        expected_query = item.get('cypher')

        if not question or not expected_query:
            console.print(f"[yellow]Skipping item {i+1}: Missing question or expected query.[/]")
            continue

        console.print(f"\n[bold]Processing Example {i+1}/{len(data)}[/]")
        console.print(f"[question] {question}")
        console.print(f"[expected_cypher] {expected_query}")

        generated_query = None
        is_match = False
        try:
            prompt = f"Generate a Cypher query for the following question about a medical graph database: {question}. Only return the Cypher query."
            message_history = chat_instance.send_message(text=prompt)

            generated_query = extract_cypher_query(message_history)

            if generated_query:
                query_found_count += 1
                console.print(f"[generated_cypher] {generated_query}")
                norm_gen = ' '.join(generated_query.strip().split()).lower()
                norm_exp = ' '.join(expected_query.strip().split()).lower()
                is_match = norm_gen == norm_exp
            else:
                 console.print("[bold yellow]⚠️ Could not extract generated Cypher query from response.[/]")


        except Exception as e:
            console.print(f"[bold red]Error processing example {i+1}: {e}[/]")

        if is_match:
            correct_matches += 1
            console.print("[bold green]✔️ Exact Match[/]")
        elif generated_query: # Only print No Match if we actually got a query
            console.print("[bold red]❌ No Match[/]")

        results.append({
            "question": question,
            "expected": expected_query,
            "generated": generated_query if generated_query else "ERROR/NONE",
            "match": is_match,
        })


    accuracy = (correct_matches / query_found_count) * 100 if query_found_count > 0 else 0
    console.print(f"\n[bold cyan]Benchmark Complete for '{dataset_name}'[/]")
    console.print(f"[bold]Generated Query Found: {query_found_count}/{len(data)}[/]")
    console.print(f"[bold]Exact Match Accuracy (on found queries): {accuracy:.2f}% ({correct_matches}/{query_found_count})[/]")
    
    if schema_command_found and original_schema_func:
        for command in agent_instance.commands:
            if command.name == 'neo4j_database_schema':
                command.function = original_schema_func
                console.print(f"[info] Restored original function for '{command.name}'.")
                break
            
    if cypher_command_found and original_cypher_func:
        for command in agent_instance.commands:
            if command.name == 'neo4j_database_cypher_query':
                command.function = original_cypher_func
                console.print(f"[info] Restored original function for '{command.name}'.")
                break
            
    if prop_values_command_found and original_prop_values_func:
        for command in agent_instance.commands:
            if command.name == 'neo4j_database_node_property_values':
                command.function = original_prop_values_func
                console.print(f"[info] Restored original function for '{command.name}'.")
                break
            
    if sample_nodes_command_found and original_sample_nodes_func:
        for command in agent_instance.commands:
            if command.name == 'neo4j_database_sample_nodes':
                command.function = original_sample_nodes_func
                console.print(f"[info] Restored original function for '{command.name}'.")
                break
            

def normalize(query: str) -> str:
    return ' '.join(query.strip().split()).lower()


def run_benchmark_cypherbench(agent_instance: Agent, db_provider_instance: DBProvider, dataset_split: str = "train"):

    loader = CypherBenchLoader(split=dataset_split, offset=0, length=100)
    data = loader.available_data()
    rows = data.get("rows", [])
    
    console.print(f"\n[bold cyan]Running benchmark on CypherBench '{dataset_split}' set ({len(rows)} examples)...[/]")

    results = []
    correct_matches = 0
    query_found_count = 0

    llm_to_test = LLMType.GEMINI
    chat_id_model = db_provider_instance.chat.create_chat_model(llm_type=llm_to_test)
    chat_id = chat_id_model.id
    console.print(f"[info]Created temporary chat ID for CypherBench benchmark: {chat_id} using {llm_to_test}")

    chat_instance = Chat(db_provider=db_provider_instance, agent=agent_instance, id=chat_id)
    
    if not rows:
        console.print("[bold red]DEBUG: The 'rows' list is empty after loading data.[/]")
        return
    console.print(f"[blue]DEBUG: Structure of the first row: {rows[0] if rows else 'N/A'}[/]")

    for i, item in enumerate(rows):
        row_data = item.get('row', {}) 
        question = row_data.get("nl_question")
        expected_query = row_data.get("gold_cypher")

        console.print(f"[blue]DEBUG: Extracted question: {repr(question)}[/]")
        console.print(f"[blue]DEBUG: Extracted expected_query: {repr(expected_query)}[/]")

        if not question or not expected_query:
            console.print(f"[yellow]Skipping item {i+1}: Missing question or expected query in row_data: {row_data}.[/]") # Added row_data to skip message
            continue

        console.print(f"\n[bold]Processing Example {i+1}/{len(rows)}[/]")
        console.print(f"[question] {question}")
        console.print(f"[expected_cypher] {expected_query}")

        generated_query = None
        is_match = False
        try:
            # Construct a prompt for the LLM.
            prompt = f"Generate a Cypher query for the following question: {question}. Only return the Cypher query."
            message_history = chat_instance.send_message(text=prompt)
            generated_query = extract_cypher_query(message_history)
            if generated_query:
                query_found_count += 1
                console.print(f"[generated_cypher] {generated_query}")
                if normalize(generated_query) == normalize(expected_query):
                    is_match = True
                    correct_matches += 1
                    console.print("[bold green]Exact Match[/]")
                else:
                    console.print("[bold red]Mismatch[/]")
            else:
                console.print("[bold yellow]Could not extract generated Cypher query.[/]")
        except Exception as e:
            console.print(f"[bold red]Error processing example {i+1}: {e}[/]")

        results.append({
            "question": question,
            "expected": expected_query,
            "generated": generated_query if generated_query else "ERROR/NONE",
            "match": is_match,
        })

    accuracy = (correct_matches / query_found_count) * 100 if query_found_count > 0 else 0
    console.print(f"\n[bold cyan]CypherBench Benchmark Complete[/]")
    console.print(f"[bold]Generated Query Found: {query_found_count}/{len(rows)}[/]")
    console.print(f"[bold]Exact Match Accuracy (on found queries): {accuracy:.2f}% ({correct_matches}/{query_found_count})[/]")



if __name__ == "__main__":
    agent_instance, db_provider_instance = initialize_rag_system()
    if not os.getenv('MONGO_URI'):
        console.print("[bold red]Error: MONGO_URI environment variable not set. Database connection required.[/]")
    else:
        # run_benchmark_spcql(agent_instance, db_provider_instance, dataset_name="dev") # Or "test"
        run_benchmark_cypherbench(agent_instance, db_provider_instance, dataset_split="train")
