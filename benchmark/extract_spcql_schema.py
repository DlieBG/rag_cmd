import re
import json
from spcql import SPCQLLoader

def extract_node_label(node_str):
    node_str = node_str.strip()
    match = re.search(r":\s*([A-Za-z0-9_]+)", node_str)
    if match:
        return match.group(1)
    return "UNKNOWN"

def parse_cypher(cypher):
    import re
    match_clause = re.search(r"match\s+(.*?)(?:return)", cypher, re.IGNORECASE | re.DOTALL)
    clause = match_clause.group(1) if match_clause else cypher

    pattern = r"(\([^\)]+\))\s*[-–]\s*\[([^\]]+)\]\s*[-–>]+\s*(\([^\)]+\))"
    results = re.findall(pattern, clause, re.IGNORECASE)
    edges = []
    for source_str, rel_str, target_str in results:
        source_label = extract_node_label(source_str)
        target_label = extract_node_label(target_str)
        rel_match = re.search(r":\s*([^\s\[\]]+)", rel_str)
        rel_type = rel_match.group(1) if rel_match else "UNKNOWN"
        edges.append((source_label, rel_type, target_label))
    return edges


def aggregate_schema(loader):
    schema = {
        "nodes": {},        
        "relationships": {}   
    }
    datasets = loader.available_sets()
    for ds in datasets:
        data = loader.get_data(ds)
        for i, item in enumerate(loader.get_data(ds)):
            cypher = item.get("cypher", "")
            edges = parse_cypher(cypher)
            for src, rel, tgt in edges:

                if src not in schema["nodes"]:
                    schema["nodes"][src] = {
                        "properties": {"name": "String"},
                        "relationships": {"out": {}, "in": {}}
                    }

                if tgt not in schema["nodes"]:
                    schema["nodes"][tgt] = {
                        "properties": {"name": "String"},
                        "relationships": {"out": {}, "in": {}}
                    }

                out_rels = schema["nodes"][src]["relationships"]["out"]
                if rel not in out_rels:
                    out_rels[rel] = set()
                out_rels[rel].add(tgt)
                
                in_rels = schema["nodes"][tgt]["relationships"]["in"]
                if rel not in in_rels:
                    in_rels[rel] = set()
                in_rels[rel].add(src)
                

                key = f"{src}-{rel}->{tgt}"
                schema["relationships"][key] = {"type": rel, "from": src, "to": tgt}
    

    for node, node_data in schema["nodes"].items():
        for direction in ["out", "in"]:
            for rel in node_data["relationships"][direction]:
                node_data["relationships"][direction][rel] = sorted(list(node_data["relationships"][direction][rel]))
    
    return schema

if __name__ == "__main__":
    loader = SPCQLLoader()
    schema = aggregate_schema(loader)
    print(json.dumps(schema, indent=4, ensure_ascii=False))
    output_filename = "benchmark/inferred_spcql_schema.json"
    try:
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(schema, f, indent=4, ensure_ascii=False)
        print(f"\n[INFO] Inferred schema saved to {output_filename}")
    except Exception as e:
        print(f"\n[ERROR] Failed to save schema: {e}")
