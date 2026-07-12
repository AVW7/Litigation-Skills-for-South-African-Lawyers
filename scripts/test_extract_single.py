import json
import subprocess
from pathlib import Path
import sys

# Load chunk info
chunks = json.loads(Path('graphify-out/.graphify_chunks_info.json').read_text(encoding='utf-8'))
files = chunks[0][:8]  # first 8 files only

# Load prompt template
spec_text = Path('/Users/ajadvanwyk/.gemini/config/skills/graphify/references/extraction-spec.md').read_text(encoding='utf-8')
start_idx = spec_text.find("```\n") + 4
end_idx = spec_text.rfind("\n```")
prompt_template = spec_text[start_idx:end_idx].strip()

file_list_str = ""
file_contents_str = "\n--- FILE CONTENTS ---\n"
for f in files:
    file_path = Path(f)
    if file_path.exists():
        file_list_str += f"- {f}\n"
        if file_path.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tiff'):
            content = file_path.read_text(encoding='utf-8', errors='replace')
            file_contents_str += f"\nFile: {f}\n```\n{content}\n```\n"

prompt = prompt_template
prompt = prompt.replace("CHUNK_NUM", "1")
prompt = prompt.replace("TOTAL_CHUNKS", "31")
prompt = prompt.replace("FILE_LIST", file_list_str + file_contents_str)
prompt = prompt.replace("DEEP_MODE", "False")
prompt = prompt.replace("CHUNK_PATH", str(Path('graphify-out/.graphify_chunk_001.json').resolve()))
prompt += "\n\nCRITICAL: Do NOT attempt to write this JSON to disk using any tool. Instead, output the raw JSON directly in your message response. Your entire response must be ONLY the JSON object, or a single markdown code block containing only the JSON."

print("Running single_extract.py via internal venv python for 8 files...")
cmd = ["/Users/ajadvanwyk/.hermes/hermes-agent/venv/bin/python3", "scripts/single_extract.py"]
proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True)
print("Return code:", proc.returncode)
print("STDOUT length:", len(proc.stdout))
print("STDOUT:")
print(proc.stdout)
print("STDERR:")
print(proc.stderr)
