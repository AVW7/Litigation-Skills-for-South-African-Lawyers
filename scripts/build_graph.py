import os
import sys
import json
import glob
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# Add graphify to python path if needed (using the uv tools environment)
sys.path.append("/Users/ajadvanwyk/.local/share/uv/tools/graphifyy/lib/python3.14/site-packages")

import importlib

# Dynamically import to satisfy static checkers/linters
graphify_extract = importlib.import_module("graphify.extract")
collect_files = graphify_extract.collect_files
extract = graphify_extract.extract

graphify_build = importlib.import_module("graphify.build")
build_from_json = graphify_build.build_from_json

graphify_cluster = importlib.import_module("graphify.cluster")
cluster = graphify_cluster.cluster
score_all = graphify_cluster.score_all

graphify_analyze = importlib.import_module("graphify.analyze")
god_nodes = graphify_analyze.god_nodes
surprising_connections = graphify_analyze.surprising_connections
suggest_questions = graphify_analyze.suggest_questions

graphify_report = importlib.import_module("graphify.report")
generate = graphify_report.generate

graphify_export = importlib.import_module("graphify.export")
to_json = graphify_export.to_json

graphify_detect = importlib.import_module("graphify.detect")
save_manifest = graphify_detect.save_manifest


def main():
    print("--- STEP 1: AST Extraction for Code Files ---")
    detect_path = Path('graphify-out/.graphify_detect.json')
    if not detect_path.exists():
        print("Error: graphify-out/.graphify_detect.json not found. Run parallel_extract first.")
        sys.exit(1)
        
    detect = json.loads(detect_path.read_text(encoding="utf-8"))
    code_files = []
    for f in detect.get('files', {}).get('code', []):
        code_files.extend(collect_files(Path(f)) if Path(f).is_dir() else [Path(f)])
        
    if code_files:
        print(f"Extracting AST for {len(code_files)} code files...")
        result = extract(code_files, cache_root=Path('.'))
        Path('graphify-out/.graphify_ast.json').write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"AST: {len(result['nodes'])} nodes, {len(result['edges'])} edges")
    else:
        Path('graphify-out/.graphify_ast.json').write_text(
            json.dumps({'nodes':[],'edges':[],'input_tokens':0,'output_tokens':0}, ensure_ascii=False), encoding="utf-8"
        )
        print("No code files - skipped AST extraction")

    print("\n--- STEP 2: Merge Semantic Chunks ---")
    chunks = sorted(glob.glob('graphify-out/.graphify_chunk_*.json'))
    print(f"Found {len(chunks)} chunk files to merge.")
    all_nodes, all_edges, all_hyperedges = [], [], []
    total_in, total_out = 0, 0
    for c in chunks:
        try:
            d = json.loads(Path(c).read_text(encoding="utf-8"))
            all_nodes += d.get('nodes', [])
            all_edges += d.get('edges', [])
            all_hyperedges += d.get('hyperedges', [])
            total_in += d.get('input_tokens', 0)
            total_out += d.get('output_tokens', 0)
        except Exception as e:
            print(f"Warning: failed to read chunk {c}: {e}")
            
    Path('graphify-out/.graphify_semantic.json').write_text(json.dumps({
        'nodes': all_nodes, 'edges': all_edges, 'hyperedges': all_hyperedges,
        'input_tokens': total_in, 'output_tokens': total_out,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Merged semantic results: {len(all_nodes)} nodes, {len(all_edges)} edges")

    print("\n--- STEP 3: Merge AST & Semantic Extraction ---")
    ast = json.loads(Path('graphify-out/.graphify_ast.json').read_text(encoding="utf-8"))
    sem = json.loads(Path('graphify-out/.graphify_semantic.json').read_text(encoding="utf-8"))
    
    seen = {n['id'] for n in ast['nodes']}
    merged_nodes = list(ast['nodes'])
    for n in sem['nodes']:
        if n['id'] not in seen:
            merged_nodes.append(n)
            seen.add(n['id'])
            
    merged_edges = ast['edges'] + sem['edges']
    merged_hyperedges = sem.get('hyperedges', [])
    extraction = {
        'nodes': merged_nodes,
        'edges': merged_edges,
        'hyperedges': merged_hyperedges,
        'input_tokens': sem.get('input_tokens', 0),
        'output_tokens': sem.get('output_tokens', 0),
    }
    Path('graphify-out/.graphify_extract.json').write_text(
        json.dumps(extraction, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Merged extraction: {len(merged_nodes)} nodes, {len(merged_edges)} edges ({len(ast['nodes'])} AST + {len(sem['nodes'])} semantic)")

    print("\n--- STEP 4: Build Graph & Run Clustering ---")
    G = build_from_json(extraction, root='vault', directed=False)
    if G.number_of_nodes() == 0:
        print("ERROR: Graph is empty - extraction produced no nodes.")
        sys.exit(1)
        
    communities = cluster(G)
    cohesion = score_all(G, communities)
    tokens = {'input': extraction.get('input_tokens', 0), 'output': extraction.get('output_tokens', 0)}
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    
    # Export graph JSON
    wrote = to_json(G, communities, 'graphify-out/graph.json')
    if not wrote:
        print("ERROR: refused to shrink graphify-out/graph.json (existing graph is larger). Use force if needed.")
        sys.exit(1)
        
    print(f"Graph built successfully: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities.")

    print("\n--- STEP 5: Label Communities via Hermes ---")
    labels = {}
    for cid, nodes in communities.items():
        node_labels = [G.nodes[nid].get('label', nid) for nid in nodes]
        print(f"Labeling community {cid} ({len(node_labels)} nodes)...")
        label_name = label_community_with_hermes(node_labels)
        if not label_name:
            label_name = f"Community {cid}"
        labels[cid] = label_name
        print(f"-> Assigned label: {label_name}")
        
    # Regenerate suggested questions with real labels
    questions = suggest_questions(G, communities, labels)
    
    # Generate report
    report = generate(G, communities, cohesion, labels, gods, surprises, detect, tokens, 'vault', suggested_questions=questions)
    Path('graphify-out/GRAPH_REPORT.md').write_text(report, encoding="utf-8")
    Path('graphify-out/.graphify_labels.json').write_text(
        json.dumps({str(k): v for k, v in labels.items()}, ensure_ascii=False), encoding="utf-8"
    )
    print("GRAPH_REPORT.md and labels JSON written.")

    print("\n--- STEP 6: Export HTML Visualization ---")
    try:
        subprocess.run(["/Users/ajadvanwyk/.local/share/uv/tools/graphifyy/bin/graphify", "export", "html"], check=True)
        print("graph.html generated.")
    except Exception as e:
        print(f"Warning: failed to export HTML: {e}")

    print("\n--- STEP 7: Save Manifest & Cost Tracker ---")
    save_manifest(detect.get('all_files') or detect['files'], root='vault')
    
    cost_path = Path('graphify-out/cost.json')
    if cost_path.exists():
        cost = json.loads(cost_path.read_text(encoding="utf-8"))
    else:
        cost = {'runs': [], 'total_input_tokens': 0, 'total_output_tokens': 0}
        
    cost['runs'].append({
        'date': datetime.now(timezone.utc).isoformat(),
        'input_tokens': tokens['input'],
        'output_tokens': tokens['output'],
        'files': detect.get('total_files', 0),
    })
    cost['total_input_tokens'] += tokens['input']
    cost['total_output_tokens'] += tokens['output']
    cost_path.write_text(json.dumps(cost, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"Cost tracker updated. Total runs: {len(cost['runs'])}")
    print(f"All time tokens: {cost['total_input_tokens']:,} in / {cost['total_output_tokens']:,} out")

    print("\n--- STEP 8: Cleanup Temporary Files ---")
    temp_files = [
        'graphify-out/.graphify_detect.json',
        'graphify-out/.graphify_extract.json',
        'graphify-out/.graphify_ast.json',
        'graphify-out/.graphify_semantic.json',
        'graphify-out/.graphify_analysis.json',
        'graphify-out/.needs_update'
    ]
    for tf in temp_files:
        Path(tf).unlink(missing_ok=True)
        
    for tf in Path('graphify-out').glob('.graphify_chunk_*.json'):
        tf.unlink(missing_ok=True)
        
    print("Cleanup completed successfully.")

def label_community_with_hermes(nodes):
    labels_list = ", ".join(nodes[:20])
    prompt = f"""You are a community labeling agent. Look at the following list of nodes that participate in a community in the South African Litigation Skills codebase/vault:
{labels_list}

Generate a short, 2-5 word plain-language descriptive name (e.g. "Trial Preparation", "Etiquette & Protocol", "Pleadings & Drafting", "Evidence & Witnesses") that summarizes this community. Output ONLY the generated name and absolutely nothing else.
"""
    cmd = ["/Users/ajadvanwyk/.hermes/hermes-agent/venv/bin/python3", "scripts/single_extract.py"]
    try:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, check=True)
        name = proc.stdout.strip()
        if "```" in name:
            name = name.split("```")[-2].strip()
            if name.startswith("json\n"):
                name = name[5:].strip()
        return name
    except Exception as e:
        print(f"Failed to query Hermes for labeling: {e}")
        return None

if __name__ == "__main__":
    main()
