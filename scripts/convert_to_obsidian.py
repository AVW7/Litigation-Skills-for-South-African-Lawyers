import os
import re
import json

# Define paths
WORKSPACE_DIR = "/Users/ajadvanwyk/Downloads/Litigation Skills for South African Lawyers.pdf"
PAGES_DIR = os.path.join(WORKSPACE_DIR, "pages")
VAULT_DIR = os.path.join(WORKSPACE_DIR, "vault")
VAULT_PAGES_DIR = os.path.join(VAULT_DIR, "Pages")
VAULT_RULES_DIR = os.path.join(VAULT_DIR, "Rules")
DATA_FILE = os.path.join(WORKSPACE_DIR, "dashboard", "public", "vault_data.json")

# Predefined chapters mapping for safety fallback
CHAPTERS_MAP = {
    1: "Interviewing clients and witnesses",
    2: "Advising and counselling clients",
    3: "Alternatives to litigation",
    4: "Preparing to commence action",
    5: "Function, form and style of pleadings",
    6: "Drafting statements of claim",
    7: "Drafting pleas and special pleas",
    8: "Drafting replications and further pleadings",
    9: "Drafting exceptions, applications to strike out and objections to a charge",
    10: "Drafting applications",
    11: "Preparing the case for trial: Advice on evidence",
    12: "Preparing the case for trial: Assembling the evidence",
    13: "Preparation for trial: Legal research",
    14: "Preparation for trial: Fact analysis and strategy",
    15: "The protocol and etiquette of the courtroom",
    16: "Opening statement",
    17: "Examination-in-chief",
    18: "Cross-examination",
    19: "Re-examination",
    20: "Special procedures",
    21: "Closing argument",
    22: "Motion Court",
    23: "Persuasive advocacy: Substance and style",
    24: "Reviews",
    25: "Appeals"
}

def clean_ocr(text):
    # Fix common spacing issues
    text = re.sub(r'([a-z])-\n([a-z])', r'\1\2', text) # hyphens at end of line
    return text

def parse_pages():
    # Pass 1: Build file lists and mapping from printed page -> pdf page
    pages_data = []
    printed_to_pdf = {}
    
    # We expect folders page-1 to page-319
    for i in range(1, 320):
        page_folder = os.path.join(PAGES_DIR, f"page-{i}")
        page_file = os.path.join(page_folder, "markdown.md")
        
        if not os.path.exists(page_file):
            continue
            
        with open(page_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find printed pages in content
        # Usually marked like [Page 8]
        printed_pages = [int(p) for p in re.findall(r'\[Page\s+(\d+)\]', content)]
        
        pages_data.append({
            "pdf_page": i,
            "raw_content": content,
            "printed_pages": printed_pages
        })
        
        for pp in printed_pages:
            printed_to_pdf[pp] = i
            
    # Fill in missing printed page mappings by interpolation
    last_printed = 0
    for i in range(1, 320):
        matches = [p["printed_pages"] for p in pages_data if p["pdf_page"] == i]
        if matches and matches[0]:
            last_printed = matches[0][-1]
        else:
            # Check if we can approximate
            if last_printed > 0:
                printed_to_pdf[last_printed + 1] = i
                last_printed += 1

    return pages_data, printed_to_pdf

def run_conversion():
    os.makedirs(VAULT_PAGES_DIR, exist_ok=True)
    os.makedirs(VAULT_RULES_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    pages_raw, printed_to_pdf = parse_pages()
    
    # State tracking for chapter
    current_chapter_num = None
    current_chapter_title = "Introduction & Prefaces"
    
    # List of structured page info for base files and JSON
    processed_pages = []
    
    # Parse rules from agents.md to populate Rules.base
    rules = []
    agents_file = os.path.join(WORKSPACE_DIR, "agents.md")
    if os.path.exists(agents_file):
        with open(agents_file, 'r', encoding='utf-8') as f:
            agents_content = f.read()
        # Parse sections
        rule_sections = re.split(r'##\s+\d+\.\s+', agents_content)
        category_names = ["General", "Professional Conduct & Ethical Duties", "Courtroom Protocol & Etiquette", "Rules of Pleadings & Drafting", "Trial Advocacy & Courtroom Strategies", "Citations of Legal Authorities"]
        
        for idx, sec in enumerate(rule_sections):
            if idx == 0:
                continue # Header preamble
            lines = sec.strip().split('\n')
            category = category_names[idx] if idx < len(category_names) else "Etiquette"
            title = lines[0].strip() if lines else "Rule Section"
            body = '\n'.join(lines[1:]).strip()
            
            rule_id = f"rule-{idx}"
            rules.append({
                "id": rule_id,
                "title": title,
                "category": category,
                "content": body
            })
            
            # Write rule file to vault
            rule_file_path = os.path.join(VAULT_RULES_DIR, f"{rule_id}.md")
            with open(rule_file_path, 'w', encoding='utf-8') as rf:
                rf.write(f"---\ntitle: \"{title}\"\ncategory: \"{category}\"\nsource: \"agents.md\"\n---\n\n# {title}\n\n{body}\n")
    
    # Pass 2: Rewrite pages
    for item in pages_raw:
        pdf_page = item["pdf_page"]
        content = item["raw_content"]
        printed = item["printed_pages"]
        printed_page_val = printed[0] if printed else (pdf_page - 2 if pdf_page > 2 else "") # approximate printed page
        
        # Clean text
        content = clean_ocr(content)
        
        # Detect Chapter header
        # Patterns like: "## Chapter 3" followed by title on next line, or "## Chapter 6 Drafting..."
        chapter_match = re.search(r'(?:^|\n)(?:##|#|###)\s*Chapter\s+(\d+)\s*(.*)', content, re.IGNORECASE)
        if chapter_match:
            current_chapter_num = int(chapter_match.group(1))
            ch_title = chapter_match.group(2).strip()
            if not ch_title:
                # Look at next lines
                rest = content[chapter_match.end():].strip().split('\n')
                ch_title = rest[0].strip() if rest else ""
            
            current_chapter_title = f"Chapter {current_chapter_num}: {ch_title or CHAPTERS_MAP.get(current_chapter_num, '')}"
        else:
            # Check other headers like "## Interviewing clients and witnesses"
            header_match = re.search(r'(?:^|\n)##\s+([A-Za-z][A-Za-z\s&:]+)(?:\n|$)', content)
            if header_match:
                candidate = header_match.group(1).strip()
                if "Interviewing clients" in candidate:
                    current_chapter_num = 1
                    current_chapter_title = "Chapter 1: Interviewing clients and witnesses"
                elif "Advising and counselling" in candidate:
                    current_chapter_num = 2
                    current_chapter_title = "Chapter 2: Advising and counselling clients"
                elif "Cross-examination" in candidate and "Chapter" not in content:
                    current_chapter_num = 18
                    current_chapter_title = "Chapter 18: Cross-examination"
        
        # Format inline pages links: e.g. "page 141" -> [[Page-X|page Y]]
        def link_replacer(match):
            val = int(match.group(1))
            if val in printed_to_pdf:
                target_pdf = printed_to_pdf[val]
                return f"[[Page-{target_pdf}|page {val}]]"
            return match.group(0)
            
        content = re.sub(r'\bpages?\s+(\d+)\b', link_replacer, content, flags=re.IGNORECASE)
        
        # Format checklists ☐ or [ ]
        content = re.sub(r'(?:☐|\[\s*\])\s*', r'- [ ] ', content)
        
        # Put Protocol & Ethics sections in custom Callouts
        # e.g., lines starting with Protocol or Ethics
        lines = content.split('\n')
        in_protocol = False
        new_lines = []
        for line in lines:
            if "Protocol" in line or "Ethics" in line or "PROTOCOL" in line or "ETHICS" in line:
                if line.startswith("- [ ]") or line.startswith("##") or line.startswith("###") or line.strip().startswith("☐"):
                    in_protocol = True
                    # Strip symbols and make callout header
                    clean_line = re.sub(r'^(?:-\s*\[\s*\]|##+|#|☐)\s*', '', line).strip()
                    new_lines.append(f"> [!warning] {clean_line}")
                    continue
            
            if in_protocol:
                if line.strip() == "" or line.startswith("#"):
                    in_protocol = False
                    new_lines.append(line)
                else:
                    # Strip checkbox if any, and indent
                    clean_line = re.sub(r'^(-\s*\[\s*\]|☐)\s*', '', line).strip()
                    new_lines.append(f"> {clean_line}")
            else:
                new_lines.append(line)
                
        content = '\n'.join(new_lines)
        
        # Grab first heading for title
        headings = re.findall(r'^#+\s+(.*)', content, re.MULTILINE)
        inferred_title = headings[0].strip() if headings else f"Page {pdf_page}"
        inferred_title = re.sub(r'\[Page\s+\d+\]', '', inferred_title).strip()
        if not inferred_title:
            inferred_title = f"Page {pdf_page}"
            
        # Create Obsidian frontmatter
        frontmatter = f"""---
title: "{inferred_title}"
pdfPage: {pdf_page}
printedPage: {printed_page_val}
chapter: "{current_chapter_title}"
tags:
  - page
  - litigation-skills
  - chapter-{current_chapter_num or 0}
aliases:
  - "Page {pdf_page}"
  - "PDF Page {pdf_page}"
---

"""
        # Page Navigation
        prev_link = f"[[Page-{pdf_page-1}|← Previous Page]]" if pdf_page > 1 else "← Start"
        next_link = f"[[Page-{pdf_page+1}|Next Page →]]" if pdf_page < 319 else "End →"
        nav_header = f"{prev_link} | [[Dashboard|Dashboard]] | {next_link}\n\n---\n\n"
        nav_footer = f"\n\n---\n\n{prev_link} | [[Dashboard|Dashboard]] | {next_link}"
        
        full_note = frontmatter + nav_header + content + nav_footer
        
        # Write markdown file
        note_name = f"Page-{pdf_page}.md"
        note_path = os.path.join(VAULT_PAGES_DIR, note_name)
        with open(note_path, 'w', encoding='utf-8') as nf:
            nf.write(full_note)
            
        processed_pages.append({
            "filename": note_name,
            "title": inferred_title,
            "pdfPage": pdf_page,
            "printedPage": printed_page_val,
            "chapter": current_chapter_title,
            "chapterNum": current_chapter_num,
            "tags": ["page", "litigation-skills", f"chapter-{current_chapter_num or 0}"],
            "content": content
        })
        
    # Write Dashboard.md
    dashboard_content = """---
title: "Dashboard Overview"
tags:
  - dashboard
  - litigation-skills
---

# Litigation Skills for South African Lawyers
## Digital Vault Dashboard

Welcome to the digital, interactive vault for Chris Marnewick SC's *Litigation Skills for South African Lawyers*. This vault transforms the 319 pages of the text into a fully linked knowledge base.

> [!important] Court Protocol
> This workspace is governed by the rules and protocols in [[rules|South African Litigation Rules & Etiquette]]. Always address the bench with appropriate deference ("My Lord", "My Lady" in the High Court, and "Your Worship" in the Magistrates' Court).

### Database Views (Bases)
* **[[Pages.base|Pages Database]]** - View and filter all 319 pages.
* **[[Chapters.base|Chapters Index]]** - Browse chapters and starting pages.
* **[[Rules.base|Etiquette Checklists]]** - Look up professional conduct guidelines.

### Chapters Table of Contents
| Chapter | Topic | Starting Page |
|---|---|---|
| Chapter 1 | [[Page-3\|Interviewing clients and witnesses]] | 3 |
| Chapter 2 | [[Page-22\|Advising and counselling clients]] | 22 |
| Chapter 3 | [[Page-30\|Alternatives to litigation]] | 30 |
| Chapter 4 | [[Page-41\|Preparing to commence action]] | 41 |
| Chapter 5 | [[Page-47\|Function, form and style of pleadings]] | 47 |
| Chapter 6 | [[Page-54\|Drafting statements of claim]] | 54 |
| Chapter 7 | [[Page-66\|Drafting pleas and special pleas]] | 66 |
| Chapter 8 | [[Page-73\|Drafting replications and further pleadings]] | 73 |
| Chapter 9 | [[Page-75\|Drafting exceptions and striking out]] | 75 |
| Chapter 10 | [[Page-80\|Drafting applications]] | 80 |
| Chapter 11 | [[Page-92\|Preparing for trial: Advice on evidence]] | 92 |
| Chapter 12 | [[Page-100\|Preparing for trial: Assembling evidence]] | 100 |
| Chapter 13 | [[Page-109\|Preparation for trial: Legal research]] | 109 |
| Chapter 14 | [[Page-115\|Preparation for trial: Fact analysis and strategy]] | 115 |
| Chapter 15 | [[Page-126\|courtroom protocol and etiquette]] | 126 |
| Chapter 16 | [[Page-131\|Opening statement]] | 131 |
| Chapter 17 | [[Page-136\|Examination-in-chief]] | 136 |
| Chapter 18 | [[Page-145\|Cross-examination]] | 145 |
| Chapter 19 | [[Page-160\|Re-examination]] | 160 |
| Chapter 20 | [[Page-163\|Special procedures]] | 163 |
| Chapter 21 | [[Page-174\|Closing argument]] | 174 |
| Chapter 22 | [[Page-179\|Motion Court]] | 179 |
| Chapter 23 | [[Page-186\|Persuasive advocacy]] | 186 |
| Chapter 24 | [[Page-193\|Reviews]] | 193 |
| Chapter 25 | [[Page-197\|Appeals]] | 197 |

"""
    with open(os.path.join(VAULT_DIR, "Dashboard.md"), 'w', encoding='utf-8') as df:
        df.write(dashboard_content)

    # Write Pages.base
    pages_base = """filters: 'file.folder == "Pages"'
properties:
  file.name:
    displayName: "Note Name"
  pdfPage:
    displayName: "PDF Page"
  printedPage:
    displayName: "Printed Page"
  chapter:
    displayName: "Chapter"
views:
  - type: table
    name: "Pages Table"
    order:
      - file.name
      - pdfPage
      - printedPage
      - chapter
"""
    with open(os.path.join(VAULT_DIR, "Pages.base"), 'w', encoding='utf-8') as bf:
        bf.write(pages_base)

    # Write Chapters.base
    chapters_base = """filters: 'file.name.contains("Page-") && (chapter != "")'
properties:
  chapter:
    displayName: "Chapter Name"
  pdfPage:
    displayName: "Starting Page"
views:
  - type: list
    name: "Chapters View"
    groupBy:
      property: chapter
      direction: ASC
    order:
      - chapter
      - pdfPage
"""
    with open(os.path.join(VAULT_DIR, "Chapters.base"), 'w', encoding='utf-8') as cf:
        cf.write(chapters_base)

    # Write Rules.base
    rules_base = """filters: 'file.folder == "Rules"'
properties:
  file.name:
    displayName: "Rule Title"
  category:
    displayName: "Rule Category"
  source:
    displayName: "Source"
views:
  - type: cards
    name: "Rules Gallery"
    order:
      - file.name
      - category
      - source
"""
    with open(os.path.join(VAULT_DIR, "Rules.base"), 'w', encoding='utf-8') as rf:
        rf.write(rules_base)

    # Write unified vault data JSON
    unified_data = {
        "pages": processed_pages,
        "rules": rules,
        "bases": {
            "Pages.base": {
                "schema": pages_base,
                "filters": 'file.folder == "Pages"',
                "properties": ["file.name", "pdfPage", "printedPage", "chapter"],
                "views": [{"type": "table", "name": "Pages Table"}]
            },
            "Chapters.base": {
                "schema": chapters_base,
                "filters": 'file.name.contains("Page-") && (chapter != "")',
                "properties": ["chapter", "pdfPage"],
                "views": [{"type": "list", "name": "Chapters View"}]
            },
            "Rules.base": {
                "schema": rules_base,
                "filters": 'file.folder == "Rules"',
                "properties": ["file.name", "category", "source"],
                "views": [{"type": "cards", "name": "Rules Gallery"}]
            }
        }
    }
    
    with open(DATA_FILE, 'w', encoding='utf-8') as jf:
        json.dump(unified_data, jf, indent=2)
        
    print(f"Vault created successfully! 319 pages converted. Data compiled into {DATA_FILE}")

if __name__ == "__main__":
    run_conversion()
