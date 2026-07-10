#!/usr/bin/env python3
"""
fix_vault_quality.py — Batch-improve Obsidian vault quality for the
Litigation Skills for South African Lawyers vault.

Fixes:
  1. Misused `- [ ]` checkboxes → plain `- ` bullets
  2. `[[[Page-X|page N]]]` triple-bracket artefacts → clean inline text
  3. Add concept wikilinks for key legal terms (first occurrence per page)
  4. Add `topics` frontmatter property extracted from content
  5. Normalize `- - [ ]` double-bullet artefacts

Usage:
  python scripts/fix_vault_quality.py
"""

import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VAULT_PAGES = Path(__file__).resolve().parent.parent / "vault" / "Pages"

# Chapter start pages and their canonical topic names (from the Dashboard)
CHAPTER_PAGES = {
    3: "Interviewing clients and witnesses",
    22: "Advising and counselling clients",
    30: "Alternatives to litigation",
    41: "Preparing to commence action",
    47: "Function, form and style of pleadings",
    54: "Drafting statements of claim",
    66: "Drafting pleas and special pleas",
    73: "Drafting replications and further pleadings",
    75: "Drafting exceptions and striking out",
    80: "Drafting applications",
    92: "Preparing for trial: Advice on evidence",
    100: "Preparing for trial: Assembling evidence",
    109: "Preparation for trial: Legal research",
    115: "Preparation for trial: Fact analysis and strategy",
    126: "Courtroom protocol and etiquette",
    131: "Opening statement",
    136: "Examination-in-chief",
    145: "Cross-examination",
    160: "Re-examination",
    163: "Special procedures",
    174: "Closing argument",
    179: "Motion Court",
    186: "Persuasive advocacy",
    193: "Reviews",
    197: "Appeals",
}

# Concept → (target_page, display_text) for wikilinks
# Each key is a regex pattern (case-insensitive); value is (page_num, display)
CONCEPT_LINKS = {
    r"\bcross-examination\b": (145, "cross-examination"),
    r"\bcross examination\b": (145, "cross-examination"),
    r"\bexamination-in-chief\b": (136, "examination-in-chief"),
    r"\bexamination in chief\b": (136, "examination-in-chief"),
    r"\bopening statement\b": (131, "opening statement"),
    r"\bclosing argument\b": (174, "closing argument"),
    r"\bre-examination\b": (160, "re-examination"),
    r"\bmotion court\b": (179, "Motion Court"),
    r"\bfacta probanda\b": (47, "facta probanda"),
    r"\bfacta probantia\b": (47, "facta probantia"),
    r"\bspecial plea\b": (66, "special plea"),
    r"\bspecial pleas\b": (66, "special pleas"),
    r"\bexception\b": (75, "exception"),
    r"\bstriking out\b": (75, "striking out"),
    r"\bnegotiation\b": (30, "negotiation"),
    r"\bmediation\b": (30, "mediation"),
    r"\barbitration\b": (30, "arbitration"),
    r"\blocus standi\b": (41, "locus standi"),
    r"\bcause of action\b": (54, "cause of action"),
    r"\bplea and sentence agreement\b": (30, "plea and sentence agreement"),
    r"\bcontributory negligence\b": (66, "contributory negligence"),
    r"\bpre-trial conference\b": (100, "pre-trial conference"),
    r"\bfact analysis\b": (115, "fact analysis"),
    r"\btheory of the case\b": (115, "theory of the case"),
    r"\bpersuasive advocacy\b": (186, "persuasive advocacy"),
    r"\badvice on evidence\b": (92, "advice on evidence"),
    r"\bdemonstrative exhibit": (100, "demonstrative exhibits"),
    r"\bcircumstantial evidence\b": (100, "circumstantial evidence"),
    r"\bexpert witness": (100, "expert witness"),
    r"\bexpert evidence\b": (100, "expert evidence"),
    r"\bburden of proof\b": (92, "burden of proof"),
    r"\bhearsay\b": (92, "hearsay"),
}

# Topic extraction keywords (pattern → topic tag)
TOPIC_KEYWORDS = {
    r"\bnegotiat": "negotiation",
    r"\bmediat": "mediation",
    r"\barbitrat": "arbitration",
    r"\bsettlement\b": "settlement",
    r"\bcross-examin": "cross-examination",
    r"\bexamination-in-chief\b": "examination-in-chief",
    r"\bre-examin": "re-examination",
    r"\bopening statement\b": "opening-statement",
    r"\bclosing argument\b": "closing-argument",
    r"\bpleading": "pleadings",
    r"\bexception\b": "exceptions",
    r"\bstriking out\b": "striking-out",
    r"\bapplication\b": "applications",
    r"\bmotion court\b": "motion-court",
    r"\baffidavit": "affidavits",
    r"\bjurisdiction\b": "jurisdiction",
    r"\blocus standi\b": "locus-standi",
    r"\bcause of action\b": "cause-of-action",
    r"\bcontract\b": "contract",
    r"\bdelict\b": "delict",
    r"\bnegligence\b": "negligence",
    r"\bfraud\b": "fraud",
    r"\bprescription\b": "prescription",
    r"\bevidence\b": "evidence",
    r"\bwitness\b": "witnesses",
    r"\bexpert\b": "expert-evidence",
    r"\bhearsay\b": "hearsay",
    r"\bcircumstantial\b": "circumstantial-evidence",
    r"\bdirect evidence\b": "direct-evidence",
    r"\bcredibility\b": "credibility",
    r"\bburden of proof\b": "burden-of-proof",
    r"\bonus\b": "onus",
    r"\bprotocol\b": "protocol-and-ethics",
    r"\bethics\b": "protocol-and-ethics",
    r"\bcourtroom\b": "courtroom-protocol",
    r"\betiquette\b": "courtroom-etiquette",
    r"\bappeal\b": "appeals",
    r"\breview\b": "reviews",
    r"\bsentenc": "sentencing",
    r"\bbail\b": "bail",
    r"\bconstitution": "constitutional-law",
    r"\bfact analysis\b": "fact-analysis",
    r"\btheory of the case\b": "theory-of-case",
    r"\bpersuasi": "persuasion",
    r"\brhetoric": "rhetoric",
    r"\bargument\b": "argumentation",
    r"\bdamages\b": "damages",
    r"\binterdict\b": "interdicts",
    r"\burgent\b": "urgent-applications",
    r"\bconsent to judgment\b": "consent-to-judgment",
    r"\bdiscovery\b": "discovery",
    r"\binterrogator": "interrogatories",
    r"\badmission\b": "admissions",
}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def parse_frontmatter(content: str):
    """Split file into (frontmatter_str, body_str). Returns (None, content) if no frontmatter."""
    if not content.startswith("---"):
        return None, content
    end = content.find("---", 3)
    if end == -1:
        return None, content
    fm = content[3:end].strip()
    body = content[end + 3:]
    return fm, body


def rebuild_file(fm_str: str, body: str) -> str:
    """Rebuild the file from frontmatter string and body."""
    return f"---\n{fm_str}\n---{body}"


def fix_checkboxes(body: str) -> str:
    """Convert `- [ ] ` to `- ` for prose bullet points."""
    # Fix double-bullet artefacts first: `- - [ ]` → `- `
    body = re.sub(r'^(\s*)- - \[ \] ', r'\1- ', body, flags=re.MULTILINE)
    # Convert remaining `- [ ]` to plain bullets
    body = re.sub(r'^(\s*)- \[ \] ', r'\1- ', body, flags=re.MULTILINE)
    return body


def fix_triple_brackets(body: str) -> str:
    """
    Fix `[[[Page-X|page N]]]` artefacts.
    - Standalone lines (just the triple bracket): remove entirely
    - Inline within text: replace with *(see page N)*
    """
    # Standalone lines: just the triple bracket reference, possibly with whitespace
    body = re.sub(
        r'^\s*\[\[\[Page-\d+\|page\s+\d+\]\]\]\s*$\n?',
        '',
        body,
        flags=re.MULTILINE
    )
    # Inline occurrences within text
    body = re.sub(
        r'\[\[\[Page-\d+\|(page\s+\d+)\]\]\]',
        r'*(see \1)*',
        body
    )
    return body


def add_concept_wikilinks(body: str, current_page: int) -> str:
    """
    Add wikilinks for key legal concepts. Only links first occurrence per concept.
    Skips if the text is already inside a wikilink or in frontmatter.
    Does not link a concept to its own page.
    """
    for pattern, (target_page, display) in CONCEPT_LINKS.items():
        # Don't link to self
        if target_page == current_page:
            continue

        # Don't link if this page is within 2 pages of the target
        # (the concept is already being discussed in context)
        if abs(target_page - current_page) <= 2:
            continue

        regex = re.compile(pattern, re.IGNORECASE)
        match = regex.search(body)
        if match:
            matched_text = match.group(0)
            # Check if already inside a wikilink: look for [[ before without closing ]]
            before = body[:match.start()]
            # Simple check: if the last [[ before match has no ]] between it and match
            last_open = before.rfind("[[")
            last_close = before.rfind("]]")
            if last_open > last_close:
                # Already inside a wikilink, skip
                continue

            # Check if in a heading line
            line_start = body.rfind('\n', 0, match.start()) + 1
            line = body[line_start:match.start()]
            if line.lstrip().startswith('#'):
                continue

            # Check if in frontmatter area (shouldn't be, since we only process body)
            # Replace first occurrence only
            replacement = f"[[Page-{target_page}|{matched_text}]]"
            body = body[:match.start()] + replacement + body[match.end():]

    return body


def extract_topics(body: str) -> list:
    """Extract topic tags from body content."""
    topics = set()
    body_lower = body.lower()
    for pattern, topic in TOPIC_KEYWORDS.items():
        if re.search(pattern, body_lower):
            topics.add(topic)
    # Return sorted, deduplicated
    return sorted(topics)


def add_topics_to_frontmatter(fm_str: str, topics: list) -> str:
    """Add topics property to frontmatter if not already present."""
    if not topics:
        return fm_str
    if "topics:" in fm_str:
        return fm_str  # Already has topics

    # Add topics before the end
    topics_yaml = "topics:\n" + "\n".join(f"  - {t}" for t in topics)
    fm_str = fm_str + "\n" + topics_yaml
    return fm_str


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_file(filepath: Path, stats: dict) -> None:
    """Process a single page file."""
    content = filepath.read_text(encoding="utf-8")

    # Extract page number from filename
    page_match = re.search(r'Page-(\d+)\.md$', filepath.name)
    if not page_match:
        return
    page_num = int(page_match.group(1))

    # Parse frontmatter and body
    fm_str, body = parse_frontmatter(content)
    if fm_str is None:
        print(f"  SKIP {filepath.name}: no frontmatter")
        return

    original_body = body

    # 1. Fix checkboxes
    body = fix_checkboxes(body)
    if body != original_body:
        stats["checkbox_fixes"] += 1

    # 2. Fix triple brackets
    pre_triple = body
    body = fix_triple_brackets(body)
    if body != pre_triple:
        stats["triple_bracket_fixes"] += 1

    # 3. Add concept wikilinks
    pre_links = body
    body = add_concept_wikilinks(body, page_num)
    if body != pre_links:
        stats["wikilink_additions"] += 1

    # 4. Extract topics and add to frontmatter
    topics = extract_topics(body)
    original_fm = fm_str
    fm_str = add_topics_to_frontmatter(fm_str, topics)
    if fm_str != original_fm:
        stats["topics_added"] += 1

    # Rebuild and write if changed
    new_content = rebuild_file(fm_str, body)
    if new_content != content:
        filepath.write_text(new_content, encoding="utf-8")
        stats["files_modified"] += 1


def main():
    if not VAULT_PAGES.exists():
        print(f"ERROR: Pages directory not found at {VAULT_PAGES}")
        sys.exit(1)

    page_files = sorted(VAULT_PAGES.glob("Page-*.md"),
                        key=lambda p: int(re.search(r'(\d+)', p.stem).group(1)))

    print(f"Processing {len(page_files)} page files in {VAULT_PAGES}")
    print("=" * 60)

    stats = {
        "files_modified": 0,
        "checkbox_fixes": 0,
        "triple_bracket_fixes": 0,
        "wikilink_additions": 0,
        "topics_added": 0,
    }

    for f in page_files:
        process_file(f, stats)

    print("\n" + "=" * 60)
    print("RESULTS:")
    print(f"  Files processed:        {len(page_files)}")
    print(f"  Files modified:         {stats['files_modified']}")
    print(f"  Checkbox fixes:         {stats['checkbox_fixes']}")
    print(f"  Triple bracket fixes:   {stats['triple_bracket_fixes']}")
    print(f"  Wikilink additions:     {stats['wikilink_additions']}")
    print(f"  Topics added:           {stats['topics_added']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
