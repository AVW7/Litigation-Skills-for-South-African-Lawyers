import json
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys

# Load chunk info
chunks_file = Path('graphify-out/.graphify_chunks_info.json')
if not chunks_file.exists():
    print("Error: graphify-out/.graphify_chunks_info.json not found.")
    sys.exit(1)

chunks = json.loads(chunks_file.read_text(encoding='utf-8'))
total_chunks = len(chunks)

# Load prompt template from references/extraction-spec.md
spec_file = Path('/Users/ajadvanwyk/.gemini/config/skills/graphify/references/extraction-spec.md')
if not spec_file.exists():
    spec_file = Path('graphify-out/extraction-spec.md')

spec_text = spec_file.read_text(encoding='utf-8')
start_idx = spec_text.find("```\n") + 4
end_idx = spec_text.rfind("\n```")
prompt_template = spec_text[start_idx:end_idx].strip()

# Base project path
project_root = str(Path('.').resolve())

def process_chunk(chunk_idx, files):
    chunk_num = chunk_idx + 1
    chunk_name = f"{chunk_num:03d}"
    chunk_path = f"{project_root}/graphify-out/.graphify_chunk_{chunk_name}.json"
    
    # Check if this chunk is already extracted
    if Path(chunk_path).exists():
        try:
            data = json.loads(Path(chunk_path).read_text(encoding='utf-8'))
            if "nodes" in data and "edges" in data:
                return chunk_path, True
        except Exception:
            pass

    # Provide only the list of file paths (do not inline contents to avoid OS limits)
    file_list_str = ""
    for f in files:
        file_list_str += f"- {f}\n"

    # Format the prompt
    prompt = prompt_template
    prompt = prompt.replace("CHUNK_NUM", str(chunk_num))
    prompt = prompt.replace("TOTAL_CHUNKS", str(total_chunks))
    prompt = prompt.replace("FILE_LIST", file_list_str)
    prompt = prompt.replace("DEEP_MODE", "False")
    prompt = prompt.replace("CHUNK_PATH", chunk_path)
    
    print(f"[{chunk_name}/{total_chunks}] Starting extraction for {len(files)} files...")
    
    # Run hermes CLI in one-shot mode
    cmd = ["hermes", "-z", prompt]
    
    start_time = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        stdout = proc.stdout
        elapsed = time.time() - start_time
        
        # Verify if the chunk file was successfully created on disk
        chunk_file_path = Path(chunk_path)
        if chunk_file_path.exists():
            try:
                data = json.loads(chunk_file_path.read_text(encoding='utf-8'))
                if "nodes" in data and "edges" in data:
                    print(f"[{chunk_name}/{total_chunks}] Completed in {elapsed:.1f}s. Extracted {len(data['nodes'])} nodes, {len(data['edges'])} edges.")
                    return chunk_path, True
            except Exception as e:
                print(f"[{chunk_name}/{total_chunks}] Warning: Written file invalid JSON: {e}")
        
        # Fallback: Parse stdout
        json_str = stdout.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```", 1)[1].split("```", 1)[0].strip()
            
        data = json.loads(json_str)
        if "nodes" in data and "edges" in data:
            chunk_file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
            print(f"[{chunk_name}/{total_chunks}] Completed (from stdout) in {elapsed:.1f}s. Extracted {len(data['nodes'])} nodes, {len(data['edges'])} edges.")
            return chunk_path, True
            
        print(f"[{chunk_name}/{total_chunks}] Failed: Output structure invalid. Stdout: {stdout}")
        return chunk_path, False
    except Exception as e:
        print(f"[{chunk_name}/{total_chunks}] Error occurred: {e}")
        if 'proc' in locals() and proc.stderr:
            print(f"[{chunk_name}/{total_chunks}] Stderr: {proc.stderr}")
        return chunk_path, False

# Execute in parallel
success_count = 0
results = []
print(f"Starting parallel extraction of {total_chunks} chunks with 4 workers...")
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(process_chunk, idx, files): idx for idx, files in enumerate(chunks)}
    for future in as_completed(futures):
        idx = futures[future]
        path, success = future.result()
        if success:
            success_count += 1
        results.append((idx, success))

print(f"\nExtraction finished. Successful chunks: {success_count}/{total_chunks}")
if success_count < total_chunks:
    print("Warning: Some chunks failed. You may want to re-run the script to catch missing chunks.")
    sys.exit(1)
sys.exit(0)
