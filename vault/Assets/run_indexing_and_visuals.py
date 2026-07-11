import os
import re
import glob
from pathlib import Path

VAULT_DIR = Path("/Users/ajadvanwyk/Downloads/Litigation Skills for South African Lawyers.pdf/vault")
INDEXES_DIR = VAULT_DIR / "Indexes"

ORDER = [f'L{i:02d}' for i in range(29)]
TITLES = {
    'L00': 'L00 - Introduction & Prefaces',
    'L01': 'L01 - Interviewing clients and witnesses',
    'L02': 'L02 - Advising and counselling clients',
    'L03': 'L03 - Alternatives to litigation',
    'L04': 'L04 - Preparing to commence action',
    'L05': 'L05 - Function, form and style of pleadings',
    'L06': 'L06 - Drafting statements of claim',
    'L07': 'L07 - Drafting pleas and special pleas',
    'L08': 'L08 - Drafting replications and further pleadings',
    'L09': 'L09 - Drafting exceptions and striking out',
    'L10': 'L10 - Drafting applications',
    'L11': 'L11 - Preparing the case for trial: Advice on evidence',
    'L12': 'L12 - Preparing the case for trial: Assembling the evidence',
    'L13': 'L13 - Preparation for trial: Legal research',
    'L14': 'L14 - Preparation for trial: Fact analysis and strategy',
    'L15': 'L15 - The protocol and etiquette of the courtroom',
    'L16': 'L16 - Opening statement',
    'L17': 'L17 - Examination-in-chief',
    'L18': 'L18 - Cross-examination',
    'L19': 'L19 - Re-examination',
    'L20': 'L20 - Special procedures',
    'L21': 'L21 - Closing argument',
    'L22': 'L22 - Motion Court',
    'L23': 'L23 - Persuasive advocacy',
    'L24': 'L24 - Reviews',
    'L25': 'L25 - Appeals',
    'L26': 'L26 - Epilogue',
    'L27': 'L27 - Appendices',
    'L28': 'L28 - Index'
}

def create_extra_terms():
    terms = [
        {
            "name": "Pleadings",
            "tags": ["term", "pleadings"],
            "aliases": ["pleading", "pleadings-flow"],
            "definition": "Written statements delivered alternately by the parties to a lawsuit, starting with the plaintiff's statement of claim, detailing the facts upon which they rely for their claim or defense.",
            "simple_words": "The exchange of official court documents outlining each party's story before the trial starts.",
            "analogy": "The opening declarations in a board game, setting the board and establishing rules before play starts.",
            "why_need": "To narrow down the issues in dispute and prevent either party from being caught by surprise in court.",
            "visual": "**Animated:** Pleadings exchange flow\n\n![[anim_pleadings_flow.gif]]\n\n```mermaid\ngraph LR\n    Summons[\"Summons / Claim\"] --> Intent[\"Intent to Defend\"] --> Plea[\"Plea\"] --> Rep[\"Replication\"]\n```",
            "related": "[[Facta Probanda]] · [[Facta Probantia]] · [[Cause of Action]]",
            "source": "Chapter 05 (Page 54)"
        },
        {
            "name": "Urgent Application",
            "tags": ["term", "motion-court"],
            "aliases": ["urgency", "urgent applications"],
            "definition": "An application brought in terms of High Court Rule 6(12) where standard timelines are bypassed due to immediate risk of irreparable harm or injustice.",
            "simple_words": "An emergency court case that skips the usual long waiting times.",
            "analogy": "The emergency room in a hospital. You get immediate attention because your condition is life-threatening.",
            "why_need": "To provide swift legal remedy in emergency situations where waiting for the normal court roll would render the eventual relief useless.",
            "visual": "**Animated:** Motion application exchange\n\n![[anim_motion_exchange.gif]]\n\n```mermaid\ngraph TD\n    FA[\"Founding Affidavit\"] --> AA[\"Answering Affidavit\"] --> RA[\"Replying Affidavit\"] --> Hearing[\"Court Hearing\"]\n```",
            "related": "[[Affidavit]] · [[f- Urgent Application Test]]",
            "source": "Chapter 10 (Page 99)"
        },
        {
            "name": "Onus of Proof",
            "tags": ["term", "evidence"],
            "aliases": ["burden of proof", "onus"],
            "definition": "The legal obligation on a party to prove the allegations they make in a court case.",
            "simple_words": "The duty to prove your story. If you can't prove it, you lose.",
            "analogy": "A scale. You must place enough weight on your side to tilt it.",
            "why_need": "To determine which party bears the risk of failure if the evidence is insufficient to prove the case.",
            "visual": "**Animated:** The scale of proof standards\n\n![[anim_burden_proof.gif]]\n\n```mermaid\ngraph TD\n    Civil[\"Civil: Balance of Probabilities (51%+)\"]\n    Criminal[\"Criminal: Beyond Reasonable Doubt (99%+)\"]\n```",
            "related": "[[Evidence]] · [[Witnesses]] · [[f- Negligence Test]]",
            "source": "Chapter 11 (Page 117)"
        }
    ]
    
    terms_dir = VAULT_DIR / "Terms"
    terms_dir.mkdir(parents=True, exist_ok=True)
    
    for term in terms:
        name = term["name"]
        content = f"""---
type: term
lecture: [L05, L10, L11]
tags: {term["tags"]}
aliases: {term["aliases"]}
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

## Visual

{term["visual"]}

## Related

{term["related"]}

## Source

{term["source"]}
"""
        filepath = terms_dir / f"{name}.md"
        filepath.write_text(content, encoding="utf-8")
        print(f"Created Extra Term Note: {name}")

def embed_lecture_visuals():
    # Embed trial timeline in L00
    l00_path = VAULT_DIR / "Lectures" / "L00 - Introduction & Prefaces.md"
    if l00_path.exists():
        text = l00_path.read_text(encoding="utf-8")
        if "anim_trial_timeline.gif" not in text:
            # Insert under overview
            marker = "---"
            parts = text.split(marker, 2)
            if len(parts) > 2:
                visual_block = "\n\n## Visual\n\n**Animated:** Civil Trial Timeline\n\n![[anim_trial_timeline.gif]]\n\n---\n"
                new_text = parts[0] + marker + parts[1] + visual_block + marker + parts[2]
                l00_path.write_text(new_text, encoding="utf-8")
                print("Embedded trial timeline in L00")

def link_bold_terms():
    names = {}
    for p in glob.glob(str(VAULT_DIR / 'Terms' / '*.md')):
        b = os.path.basename(p)[:-3]
        names[b.lower()] = b
        s = open(p, encoding='utf-8').read()
        m = re.search(r'^aliases:\s*\[(.*?)\]', s, re.M)
        if m:
            for a in m.group(1).split(','):
                a = a.strip().strip('"\'')
                if a and len(a) > 2:
                    names.setdefault(a.lower(), b)
                    
    tot = 0
    for path in sorted(glob.glob(str(VAULT_DIR / 'Lectures' / '*.md'))):
        raw = open(path, encoding='utf-8').read()
        fm = ''
        if raw.startswith('---'):
            e = raw.index('\n---', 3) + 4
            fm, raw = raw[:e], raw[e:]
        tok = []
        def stash(m):
            tok.append(m.group(0))
            return f'\x00{len(tok)-1}\x00'
        raw = re.sub(r'```.*?```', stash, raw, flags=re.S)
        raw = re.sub(r'`[^`\n]*`', stash, raw)
        raw = re.sub(r'!?\[\[[^\]]+\]\]', stash, raw)
        
        used = set()
        cnt = [0]
        def repl(m):
            inner = m.group(1)
            core = inner.rstrip(' .:,;)').lstrip('(')
            canon = names.get(core.lower())
            if canon and canon not in used:
                used.add(canon)
                cnt[0] += 1
                lead = inner[:len(inner)-len(inner.lstrip('('))]
                trail = inner[len(inner.rstrip(' .:,;)')):]
                link = f'[[{canon}]]' if core == canon else f'[[{canon}|{core}]]'
                return f'**{lead}{link}{trail}**'
            return m.group(0)
            
        raw = re.sub(r'\*\*([A-Za-z][^*\n]{1,48})\*\*', repl, raw)
        raw = re.sub(r'\x00(\d+)\x00', lambda m: tok[int(m.group(1))], raw)
        open(path, 'w', encoding='utf-8').write(fm + raw)
        tot += cnt[0]
        print(f"Linked terms in {os.path.basename(path)} (+{cnt[0]} links)")
    print("Total inline links created:", tot)

def build_indexes():
    terms = sorted(os.path.basename(p)[:-3] for p in glob.glob(str(VAULT_DIR / 'Terms' / '*.md')))
    formulas = sorted(os.path.basename(p)[:-3] for p in glob.glob(str(VAULT_DIR / 'Formulas' / '*.md')))
    
    os.makedirs(str(INDEXES_DIR), exist_ok=True)
    
    # 1. All Terms
    with open(str(INDEXES_DIR / 'All Terms.md'), 'w', encoding='utf-8') as f:
        f.write(f"---\ntype: index\ntags: [index]\n---\n# All Terms\n\n**{len(terms)} term notes**.\n\n")
        f.write(" · ".join(f"[[{t}]]" for t in terms) + "\n")
        
    # 2. All Formulas
    with open(str(INDEXES_DIR / 'All Formulas.md'), 'w', encoding='utf-8') as f:
        f.write(f"---\ntype: index\ntags: [index, formula]\n---\n# All Legal Tests & Rules\n\nMaster reference: **{len(formulas)}** tests.\n\n")
        for n in formulas:
            f.write(f"## [[{n}]]\n![[{n}]]\n\n")
            
    # 3. All Lectures
    with open(str(INDEXES_DIR / 'All Lectures.md'), 'w', encoding='utf-8') as f:
        f.write("---\ntype: index\ntags: [index]\n---\n# All Lectures & Chapters\n\n")
        for L in ORDER:
            f.write(f"1. [[{TITLES[L]}]]\n")
            
    # 4. Home MOC
    with open(str(VAULT_DIR / 'Home.md'), 'w', encoding='utf-8') as f:
        f.write("---\ntype: moc\ntags: [moc, home]\n---\n# South African Litigation Skills — Course Vault\n\n"
                "Interactive Obsidian vault generated from Chris Marnewick SC's *Litigation Skills for South African Lawyers*.\n\n"
                "## 📂 Core Database Views & Indexes\n"
                "- [[All Lectures]] — Ordered walkthrough of all 29 chapters\n"
                "- [[All Terms]] — Alphabetical index of core litigation concepts\n"
                "- [[All Formulas]] — Master index of key legal tests and requirements\n"
                "- [[Dashboard]] — Original document database & case index\n\n"
                "## 💡 Recommended Plugins\n"
                "- **Dataview** (`blacksmithgu`) for automated index queries.\n"
                "- **Page Preview** (core plugin) configured for plain-hover popup previews (reload Obsidian for config to take effect).\n")
    print("Indexes & Home created successfully!")

if __name__ == "__main__":
    create_extra_terms()
    embed_lecture_visuals()
    link_bold_terms()
    build_indexes()
