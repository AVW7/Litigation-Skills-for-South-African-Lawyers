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

    # Read content of all files in this chunk to provide as context
    file_list_str = ""
    file_contents_str = "\n--- FILE CONTENTS ---\n"
    for f in files:
        file_path = Path(f)
        if file_path.exists():
            file_list_str += f"- {f}\n"
            if file_path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff'):
                file_contents_str += f"\nFile: {f} (IMAGE - use view_file or similar if needed)\n"
            else:
                try:
                    content = file_path.read_text(encoding='utf-8', errors='replace')
                    file_contents_str += f"\nFile: {f}\n```\n{content}\n```\n"
                except Exception as e:
                    file_contents_str += f"\nFile: {f} (Error reading: {e})\n"
        else:
            file_list_str += f"- {f} (MISSING)\n"
            file_contents_str += f"\nFile: {f} (MISSING)\n"

    # Format the prompt
    prompt = prompt_template
    prompt = prompt.replace("CHUNK_NUM", str(chunk_num))
    prompt = prompt.replace("TOTAL_CHUNKS", str(total_chunks))
    prompt = prompt.replace("FILE_LIST", file_list_str + file_contents_str)
    prompt = prompt.replace("DEEP_MODE", "False")
    prompt = prompt.replace("CHUNK_PATH", chunk_path)
    prompt += "\n\nCRITICAL: Do NOT attempt to write this JSON to disk using any tool. Instead, output the raw JSON directly in your message response. Your entire response must be ONLY the JSON object, or a single markdown code block containing only the JSON."
    
    print(f"[{chunk_name}/{total_chunks}] Starting extraction for {len(files)} files...")
    
    # Run the custom single_extract script via the internal python virtual environment, passing prompt via stdin
    cmd = ["/Users/ajadvanwyk/.hermes/hermes-agent/venv/bin/python3", "scripts/single_extract.py"]
    
    start_time = time.time()
    try:
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, check=True)
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
print(f"Starting sequential extraction of {total_chunks} chunks (1 worker)...")
with ThreadPoolExecutor(max_workers=1) as executor:
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
