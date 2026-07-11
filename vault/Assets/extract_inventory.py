import os
import re
import json
from pathlib import Path

VAULT_DIR = Path("/Users/ajadvanwyk/Downloads/Litigation Skills for South African Lawyers.pdf/vault")
PAGES_DIR = VAULT_DIR / "Pages"

def parse_yaml_simple(yaml_text):
    data = {}
    current_key = None
    list_items = []
    
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("-"):
            val = line.lstrip("- ").strip().strip('"\'')
            list_items.append(val)
            continue
        
        if current_key and list_items:
            data[current_key] = list_items
            list_items = []
            current_key = None
            
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip().strip('"\'')
            if val == "":
                current_key = key
            else:
                data[key] = val
                
    if current_key and list_items:
        data[current_key] = list_items
        
    return data

def main():
    topics_map = {}
    
    for filepath in PAGES_DIR.glob("Page-*.md"):
        content = filepath.read_text(encoding="utf-8")
        if not content.startswith("---"):
            continue
        end = content.find("---", 3)
        if end == -1:
            continue
        fm_text = content[3:end].strip()
        fm = parse_yaml_simple(fm_text)
        
        pdf_page = int(fm.get("pdfPage", 0))
        topics = fm.get("topics", [])
        if isinstance(topics, str):
            topics = [topics]
            
        for t in topics:
            if t not in topics_map:
                topics_map[t] = []
            topics_map[t].append(pdf_page)
            
    # Sort pages for each topic
    for t in topics_map:
        topics_map[t] = sorted(list(set(topics_map[t])))
        
    print(f"Extracted {len(topics_map)} unique topics.")
    
    # Save inventory
    out_file = VAULT_DIR / "Assets" / "inventory.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(topics_map, f, indent=2)
        
    print(f"Saved inventory to {out_file}")

if __name__ == "__main__":
    main()
