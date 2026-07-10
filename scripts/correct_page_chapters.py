#!/usr/bin/env python3
import os
import re
from pathlib import Path

PAGES_DIR = Path("/Users/ajadvanwyk/Downloads/Litigation Skills for South African Lawyers.pdf/vault/Pages")

def main():
    modified_count = 0
    
    for filepath in sorted(PAGES_DIR.glob("Page-*.md"), key=lambda p: int(re.search(r'(\d+)', p.stem).group(1))):
        page_num = int(re.search(r'Page-(\d+)', filepath.name).group(1))
        content = filepath.read_text(encoding="utf-8")
        
        # Parse frontmatter
        if not content.startswith("---"):
            continue
        end = content.find("---", 3)
        if end == -1:
            continue
            
        fm_text = content[3:end]
        body_text = content[end:]
        
        # Decode and clean chapter
        chapter_match = re.search(r'chapter:\s*(.*)', fm_text)
        if not chapter_match:
            continue
            
        orig_chapter = chapter_match.group(1).strip().strip('"\'')
        new_chapter = orig_chapter
        
        # 1. Clean markdown headers inside chapter name
        new_chapter = re.sub(r'#+\s*', '', new_chapter)
        
        # 2. Correct mislabeled chapters based on page ranges
        if 194 <= page_num <= 209:
            new_chapter = "Chapter 18: Cross-examination"
        elif page_num == 285:
            new_chapter = "Epilogue"
        elif 286 <= page_num <= 299:
            new_chapter = "Appendices"
        elif 300 <= page_num <= 319:
            new_chapter = "Index"
            
        # 3. Clean up other typos / formatting
        # e.g., "Chapter 15: ### The protocol..." -> "Chapter 15: The protocol..."
        # (This is handled by the sub pattern above, but let's make it neat)
        new_chapter = new_chapter.replace("  ", " ").strip()
        
        # If changed, write back
        if new_chapter != orig_chapter:
            # Replace chapter in frontmatter
            # Handle potential quotes
            new_fm_text = fm_text.replace(chapter_match.group(0), f'chapter: "{new_chapter}"')
            new_content = f"---{new_fm_text}{body_text}"
            filepath.write_text(new_content, encoding="utf-8")
            modified_count += 1
            print(f"Page {page_num:3d}: {orig_chapter} -> {new_chapter}")
            
    print(f"Corrected chapter metadata in {modified_count} files.")

if __name__ == "__main__":
    main()
