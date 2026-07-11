import os
import re
import json
import sys
from pathlib import Path

VAULT_DIR = Path("/Users/ajadvanwyk/Downloads/Litigation Skills for South African Lawyers.pdf/vault")
PAGES_DIR = VAULT_DIR / "Pages"
TERMS_DIR = VAULT_DIR / "Terms"
FORMULAS_DIR = VAULT_DIR / "Formulas"
LECTURES_DIR = VAULT_DIR / "Lectures"
INDEXES_DIR = VAULT_DIR / "Indexes"

# Chapter mapping and ranges
CHAPTER_RANGES = [
    {"num": 0, "title": "Introduction & Prefaces", "range": range(1, 6)},
    {"num": 1, "title": "Interviewing clients and witnesses", "range": range(6, 23)},
    {"num": 2, "title": "Advising and counselling clients", "range": range(23, 33)},
    {"num": 3, "title": "Alternatives to litigation", "range": range(33, 46)},
    {"num": 4, "title": "Preparing to commence action", "range": range(46, 54)},
    {"num": 5, "title": "Function, form and style of pleadings", "range": range(54, 63)},
    {"num": 6, "title": "Drafting statements of claim", "range": range(63, 79)},
    {"num": 7, "title": "Drafting pleas and special pleas", "range": range(79, 89)},
    {"num": 8, "title": "Drafting replications and further pleadings", "range": range(89, 91)},
    {"num": 9, "title": "Drafting exceptions and striking out", "range": range(91, 98)},
    {"num": 10, "title": "Drafting applications", "range": range(98, 114)},
    {"num": 11, "title": "Preparing the case for trial: Advice on evidence", "range": range(114, 125)},
    {"num": 12, "title": "Preparing the case for trial: Assembling the evidence", "range": range(125, 136)},
    {"num": 13, "title": "Preparation for trial: Legal research", "range": range(136, 146)},
    {"num": 14, "title": "Preparation for trial: Fact analysis and strategy", "range": range(146, 163)},
    {"num": 15, "title": "The protocol and etiquette of the courtroom", "range": range(163, 172)},
    {"num": 16, "title": "Opening statement", "range": range(172, 180)},
    {"num": 17, "title": "Examination-in-chief", "range": range(180, 194)},
    {"num": 18, "title": "Cross-examination", "range": range(194, 210)},
    {"num": 19, "title": "Re-examination", "range": range(210, 213)},
    {"num": 20, "title": "Special procedures", "range": range(213, 230)},
    {"num": 21, "title": "Closing argument", "range": range(230, 239)},
    {"num": 22, "title": "Motion Court", "range": range(239, 252)},
    {"num": 23, "title": "Persuasive advocacy", "range": range(252, 263)},
    {"num": 24, "title": "Reviews", "range": range(263, 269)},
    {"num": 25, "title": "Appeals", "range": range(269, 285)},
    {"num": 26, "title": "Epilogue", "range": range(285, 286)},
    {"num": 27, "title": "Appendices", "range": range(286, 300)},
    {"num": 28, "title": "Index", "range": range(300, 320)}
]

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def strip_page_navigation(content):
    # Strip frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end+3:].strip()
            
    # Strip top navigation header (lines between --- and --- at start of body)
    lines = content.split('\n')
    cleaned_lines = []
    in_header = False
    
    # We find navigation like: [[Page-42|← Previous Page]] | [[Dashboard|Dashboard]] | [[Page-44|Next Page →]]
    for idx, line in enumerate(lines):
        if "[[Dashboard|Dashboard]]" in line:
            # Skip this line and the surrounding --- if they are close
            continue
        if line.strip() == "---" and idx < 5:
            # Skip the first separating rule
            continue
        cleaned_lines.append(line)
        
    # Reassemble and strip footer navigation
    body = '\n'.join(cleaned_lines).strip()
    # Remove final --- and anything after it if it contains Dashboard
    parts = body.rsplit('---', 1)
    if len(parts) > 1 and "[[Dashboard|Dashboard]]" in parts[1]:
        body = parts[0].strip()
        
    return body

def build_terms(terms):
    TERMS_DIR.mkdir(parents=True, exist_ok=True)
    for term in terms:
        name = term["name"]
        tags_str = ", ".join(term["tags"])
        aliases_str = ", ".join(term["aliases"])
        formulas_block = ""
        if term.get("formulas"):
            formulas_block = "\n## Formulas\n\n" + "\n".join(term["formulas"]) + "\n"
            
        content = f"""---
type: term
lecture: {term.get("lecture", [])}
tags: [{tags_str}]
aliases: [{aliases_str}]
---
# {name}

## Formal definition

{term["definition"]}

## In simple words

> [!tip] In simple words
> {term["simple_words"]}
>
> **Analogy:** {term["analogy"]}

## Why we need it

{term["why_need"]}
{formulas_block}
## Visual

{term["visual"]}

## Related

{term["related"]}

## Source

{term["source"]}
"""
        filepath = TERMS_DIR / f"{name}.md"
        filepath.write_text(content, encoding="utf-8")
        print(f"Created Term Note: {name}")

def build_formulas(formulas):
    FORMULAS_DIR.mkdir(parents=True, exist_ok=True)
    for formula in formulas:
        name = formula["name"]
        filename = formula["filename"]
        belongs_to_str = ", ".join(f'"{x}"' for x in formula["belongs_to"])
        
        symbol_rows = []
        for sym in formula["symbols"]:
            symbol_rows.append(f"| ${sym['symbol']}$ | {sym['meaning']} | {sym['role']} |")
        symbol_table = "\n".join(symbol_rows)
        
        content = f"""---
type: formula
lecture: {formula.get("lecture", [])}
tags: [formula]
belongs-to: [{belongs_to_str}]
---
# {name}

$$ {formula["latex"]} $$

## Symbol-by-symbol

| symbol | meaning | role |
|--------|---------|------|
{symbol_table}

## What it computes

{formula["computes"]}

## Why this form

{formula["why_form"]}

## Used by

{", ".join(formula["belongs_to"])}

## Source

{formula["source"]}
"""
        filepath = FORMULAS_DIR / filename
        filepath.write_text(content, encoding="utf-8")
        print(f"Created Legal Test (Formula) Note: {name}")

def build_lectures(batch_num, terms, formulas):
    LECTURES_DIR.mkdir(parents=True, exist_ok=True)
    
    # Define batch ranges
    # Batch 1: Chapters 0-5
    # Batch 2: Chapters 6-10
    # Batch 3: Chapters 11-15
    # Batch 4: Chapters 16-20
    # Batch 5: Chapters 21-28
    batches = {
        1: range(0, 6),
        2: range(6, 11),
        3: range(11, 16),
        4: range(16, 21),
        5: range(21, 29)
    }
    
    selected_chapters = batches.get(batch_num, range(0, 29))
    
    for ch_idx in selected_chapters:
        ch = CHAPTER_RANGES[ch_idx]
        ch_num = ch["num"]
        ch_title = ch["title"]
        ch_range = ch["range"]
        
        # Load all pages in chapter
        page_bodies = []
        for p in ch_range:
            page_file = PAGES_DIR / f"Page-{p}.md"
            if page_file.exists():
                page_text = page_file.read_text(encoding="utf-8")
                cleaned_body = strip_page_navigation(page_text)
                page_bodies.append(cleaned_body)
                
        chapter_body = "\n\n".join(page_bodies)
        
        # Generate Arc and flow
        prev_padded = f"{ch_num-1:02d}"
        next_padded = f"{ch_num+1:02d}"
        
        prev_title = CHAPTER_RANGES[ch_num-1]["title"] if ch_num > 0 else ""
        next_title = CHAPTER_RANGES[ch_num+1]["title"] if ch_num < 28 else ""
        
        prev_link = f"[[L{prev_padded} - {prev_title}|← Previous Chapter]]" if ch_num > 0 else "← Start"
        next_link = f"[[L{next_padded} - {next_title}|Next Chapter →]]" if ch_num < 28 else "End →"
        
        nav_line = f"Prev: {prev_link} · Next: {next_link}"
        
        # Determine some relevant terms for the lecture
        associated_terms = []
        for term in terms:
            # If the term's source mentions this chapter
            if f"Chapter {ch_num:02d}" in term["source"] or f"Chapter {ch_num}" in term["source"]:
                associated_terms.append(f"[[{term['name']}]]")
        
        concepts_line = " · ".join(associated_terms) if associated_terms else "None"
        
        # Structure the Lecture Note
        lecture_num_padded = f"{ch_num:02d}"
        lecture_title = f"L{lecture_num_padded} - {ch_title}"
        
        # Arc Box & Mermaid
        arc_box = f"""> One-paragraph overview of the litigation skills and principles taught in this chapter.
>
> [!abstract] The arc of this chapter
> **Where we left off:** We explored the previous phase of litigation or litigation foundations.
>
> This chapter covers **{ch_title}**. We look at the problem of how to execute this task, the rules that govern it, and the strategies for successful advocacy.

```mermaid
graph LR
    A["Factual/Legal Problem"] --> B["Procedural Rules / Principles"]
    B --> C["Advocacy & Drafting Strategy"]
    C --> D["Successful Courtroom Execution"]
```
*Figure: The problem-to-execution chain in this chapter.*
"""

        full_content = f"""---
type: lecture
lecture: L{ch_num}
tags: [lecture, litigation-skills]
---
# L{lecture_num_padded} — {ch_title}

{arc_box}

---

## Chapter Content Walkthrough

{chapter_body}

---

## Concepts in this lecture
{concepts_line}

## Navigation
{nav_line}
"""
        filepath = LECTURES_DIR / f"{lecture_title}.md"
        filepath.write_text(full_content, encoding="utf-8")
        print(f"Created Lecture Walkthrough: {lecture_title}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 build_study_guide.py <batch_number>")
        print("Batches:")
        print("  1: Chapters 00 - 05")
        print("  2: Chapters 06 - 10")
        print("  3: Chapters 11 - 15")
        print("  4: Chapters 16 - 20")
        print("  5: Chapters 21 - 28")
        sys.exit(1)
        
    batch_num = int(sys.argv[1])
    
    terms = load_json(VAULT_DIR / "Assets" / "terms_data.json")
    formulas = load_json(VAULT_DIR / "Assets" / "formulas_data.json")
    
    print(f"Running Build for Batch {batch_num}...")
    
    # Run only relevant sub-builds
    if batch_num == 1:
        # Build terms and formulas first as dependencies
        build_terms(terms)
        build_formulas(formulas)
        
    build_lectures(batch_num, terms, formulas)
    print(f"Batch {batch_num} build completed successfully!")

if __name__ == "__main__":
    main()
