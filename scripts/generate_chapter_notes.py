#!/usr/bin/env python3
import os
import re
from pathlib import Path

VAULT_DIR = Path("/Users/ajadvanwyk/Downloads/Litigation Skills for South African Lawyers.pdf/vault")
PAGES_DIR = VAULT_DIR / "Pages"
LIT_SKILLS_DIR = VAULT_DIR / "Litigation Skills"

def parse_yaml_simple(yaml_text):
    """Simple parser for simple YAML key-value pairs."""
    data = {}
    current_key = None
    list_items = []
    
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Check list item
        if line.startswith("-"):
            val = line.lstrip("- ").strip()
            # remove quotes if any
            val = val.strip('"\'')
            list_items.append(val)
            continue
        
        # Save previous list if any
        if current_key and list_items:
            data[current_key] = list_items
            list_items = []
            current_key = None
            
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip()
            val = val.strip('"\'')
            if val == "":
                # list starts or empty
                current_key = key
            else:
                data[key] = val
                
    if current_key and list_items:
        data[current_key] = list_items
        
    return data

def parse_page_file(filepath):
    content = filepath.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    fm_text = content[3:end].strip()
    fm = parse_yaml_simple(fm_text)
    
    # Also extract the first heading (h1, h2, h3) in the body
    body = content[end+3:].strip()
    first_heading = ""
    for line in body.splitlines():
        if line.startswith("#"):
            first_heading = line.lstrip("#").strip()
            break
            
    return {
        "filename": filepath.name,
        "title": fm.get("title", ""),
        "pdfPage": int(fm.get("pdfPage", 0)),
        "printedPage": fm.get("printedPage", ""),
        "chapter": fm.get("chapter", "Unknown"),
        "topics": fm.get("topics", []),
        "first_heading": first_heading
    }

def clean_filename(name):
    # Remove characters not allowed or inconvenient in filenames
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip()

def main():
    LIT_SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Parse all page files
    pages = []
    for filepath in PAGES_DIR.glob("Page-*.md"):
        page_info = parse_page_file(filepath)
        if page_info:
            pages.append(page_info)
            
    # Sort pages by pdfPage
    pages.sort(key=lambda x: x["pdfPage"])
    
    # 2. Group by chapter
    chapters = {}
    for p in pages:
        ch_name = p["chapter"]
        if ch_name not in chapters:
            chapters[ch_name] = []
        chapters[ch_name].append(p)
        
    print(f"Found {len(chapters)} chapters in total.")
    
    # Sort chapters. We want them in natural order.
    # Note: "Introduction & Prefaces" might be chapter 0 or similar.
    # We can sort chapters based on the pdfPage of their first page.
    sorted_chapter_names = sorted(chapters.keys(), key=lambda name: chapters[name][0]["pdfPage"])
    
    # Generate chapter overview files
    for idx, ch_name in enumerate(sorted_chapter_names):
        ch_pages = chapters[ch_name]
        start_page = ch_pages[0]["pdfPage"]
        end_page = ch_pages[-1]["pdfPage"]
        
        # Clean chapter title
        ch_num_match = re.match(r'(?:Chapter\s+(\d+)|Introduction & Prefaces)', ch_name, re.IGNORECASE)
        if ch_num_match:
            ch_num_str = ch_num_match.group(1) if ch_num_match.group(1) else "00"
            ch_num = int(ch_num_str) if ch_num_str != "00" else 0
        else:
            ch_num = idx
            ch_num_str = f"{ch_num:02d}"
            
        topic = ch_name
        if ":" in ch_name:
            topic = ch_name.split(":", 1)[1].strip()
        elif ch_name.lower().startswith("chapter"):
            parts = ch_name.split(" ", 2)
            if len(parts) > 2:
                topic = parts[2].strip()
                
        ch_num_padded = f"{ch_num:02d}"
        file_title = f"Chapter {ch_num_padded} - {topic}" if ch_num > 0 else f"Chapter 00 - {topic}"
        filename = clean_filename(file_title) + ".md"
        filepath = LIT_SKILLS_DIR / filename
        
        # Determine prev and next chapters for navigation
        prev_link = ""
        if idx > 0:
            prev_ch_name = sorted_chapter_names[idx - 1]
            p_num_match = re.match(r'(?:Chapter\s+(\d+)|Introduction & Prefaces)', prev_ch_name, re.IGNORECASE)
            p_num = int(p_num_match.group(1)) if (p_num_match and p_num_match.group(1)) else 0
            p_topic = prev_ch_name.split(":", 1)[1].strip() if ":" in prev_ch_name else prev_ch_name
            p_title = f"Chapter {p_num:02d} - {p_topic}" if p_num > 0 else f"Chapter 00 - {p_topic}"
            prev_link = f"[[{p_title}|← Previous Chapter]]"
            
        next_link = ""
        if idx < len(sorted_chapter_names) - 1:
            next_ch_name = sorted_chapter_names[idx + 1]
            n_num_match = re.match(r'(?:Chapter\s+(\d+)|Introduction & Prefaces)', next_ch_name, re.IGNORECASE)
            n_num = int(n_num_match.group(1)) if (n_num_match and n_num_match.group(1)) else 0
            n_topic = next_ch_name.split(":", 1)[1].strip() if ":" in next_ch_name else next_ch_name
            n_title = f"Chapter {n_num:02d} - {n_topic}" if n_num > 0 else f"Chapter 00 - {n_topic}"
            next_link = f"[[{n_title}|Next Chapter →]]"
            
        nav_line = " | ".join(filter(None, [prev_link, "[[Dashboard|Dashboard]]", next_link]))
        
        # Accumulate all unique topics in the chapter
        all_topics = set()
        for p in ch_pages:
            if isinstance(p["topics"], list):
                all_topics.update(p["topics"])
            elif isinstance(p["topics"], str):
                all_topics.add(p["topics"])
        sorted_topics = sorted(list(all_topics))
        
        # Build contents table
        table_rows = ["| Page (PDF) | Page (Printed) | Title / Key Content |", "| --- | --- | --- |"]
        for p in ch_pages:
            link = f"[[{p['filename'].replace('.md', '')}|Page {p['pdfPage']}]]"
            printed = p["printedPage"] if p["printedPage"] else "-"
            desc = p["title"]
            if not desc or desc.isdigit() or desc.startswith("Page"):
                desc = p["first_heading"] if p["first_heading"] else "Content"
            table_rows.append(f"| {link} | {printed} | {desc} |")
            
        topics_list_str = ", ".join(f"`{t}`" for t in sorted_topics)
        
        # Format tags and topics manually for YAML
        tags_str = "\n  - ".join(["chapter", "litigation-skills"])
        topics_str = ""
        if sorted_topics:
            topics_str = "\ntopics:\n  - " + "\n  - ".join(sorted_topics)
            
        md_content = f"""---
title: "{file_title}"
chapter: "{ch_name}"
pageRange: "{start_page}-{end_page}"
tags:
  - {tags_str}{topics_str}
---

{nav_line}

# {file_title}

> [!info] Chapter Overview
> This chapter covers PDF pages {start_page} to {end_page} of *Litigation Skills for South African Lawyers*.
> **Key Topics:** {topics_list_str if sorted_topics else "General guidance"}

## Chapter Contents

{"\n".join(table_rows)}

---

{nav_line}
"""
        filepath.write_text(md_content, encoding="utf-8")
        print(f"Created {filename}")

if __name__ == "__main__":
    main()
