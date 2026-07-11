#!/usr/bin/env python3
"""
Enhanced Mind Map Generator for South African Litigation Skills
Generates interactive HTML mind maps for each chapter with study notes
"""

import os
import json
from pathlib import Path

VAULT_PATH = Path("/Users/ajadvanwyk/Downloads/Litigation Skills for South African Lawyers.pdf/vault")
OUTPUT_DIR = VAULT_PATH / "Assets" / "mindmaps"

CHAPTER_DATA = {
    1: {
        "title": "Interviewing Clients & Witnesses",
        "icon": "people",
        "color": "#3b82f6",
        "children": [
            {
                "topic": "8-Stage Framework",
                "id": "stages",
                "children": [
                    {"topic": "1. Meeting & Pleasantries", "tip": "Meet in reception, no titles"},
                    {"topic": "2. Problem & Goal ID", "tip": "Listen first, no note-taking"},
                    {"topic": "3. Preliminary Matters", "tip": "Fees, privilege, conflicts"},
                    {"topic": "4. Chronological Facts", "tip": "Funnelling: open to closed"},
                    {"topic": "5. Case Theory", "tip": "Facta probanda vs probantia"},
                    {"topic": "6. Preliminary Advice", "tip": "Be conservative"},
                    {"topic": "7. Concluding", "tip": "Get authority, confirm letter"},
                    {"topic": "8. After Interview", "tip": "Write up immediately"}
                ]
            },
            {
                "topic": "Witness Interviews",
                "id": "witnesses",
                "children": [
                    {"topic": "Do not suggest facts", "warning": True},
                    {"topic": "Open questions only", "warning": True},
                    {"topic": "Notify opponent (GCB Rule 4.3.1)", "info": True}
                ]
            },
            {
                "topic": "Criminal Practice",
                "id": "criminal",
                "children": [
                    {"topic": "Prosecutor: Must be fair"},
                    {"topic": "s227 CPA (sex crimes)"},
                    {"topic": "Interview accused in private"}
                ]
            }
        ]
    },
    5: {
        "title": "Function, Form & Style of Pleadings",
        "icon": "document",
        "color": "#10b981",
        "children": [
            {
                "topic": "Core Principles",
                "id": "principles",
                "children": [
                    {"topic": "Facta Probanda (prove facts)", "formula": True},
                    {"topic": "Not Facta Probantia (evidence)", "warning": True},
                    {"topic": "Every pleading needs a Prayer"}
                ]
            },
            {
                "topic": "Drafting Rules",
                "id": "rules",
                "children": [
                    {"topic": "Clear and concise"},
                    {"topic": "Chronologically arranged"},
                    {"topic": "Divided into paragraphs"},
                    {"topic": "Rule 18 compliance"}
                ]
            }
        ]
    },
    18: {
        "title": "Cross-Examination",
        "icon": "scales",
        "color": "#ef4444",
        "children": [
            {
                "topic": "THE DUTY",
                "id": "duty",
                "children": [
                    {"topic": "Put your version to witness", "warning": True},
                    {"topic": "On contradicted points"},
                    {"topic": "Otherwise cannot argue contrary"}
                ]
            },
            {
                "topic": "Purposes",
                "id": "purposes",
                "children": [
                    {"topic": "Test reliability"},
                    {"topic": "Examine credibility"},
                    {"topic": "Put version"},
                    {"topic": "Elicit admissions"},
                    {"topic": "Impeach character"}
                ]
            },
            {
                "topic": "Techniques",
                "id": "techniques",
                "children": [
                    {"topic": "Use leading questions"},
                    {"topic": "Control the pace"},
                    {"topic": "One fact per question"},
                    {"topic": "Never ask 'why?'"},
                    {"topic": "Know the answer first"}
                ]
            }
        ]
    }
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chapter {chapter_num}: {title} - Mind Map</title>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../enhanced-mindmap-theme.css">
  <style>
    body {{ margin: 0; padding: 2rem; background: #0c1220; min-height: 100vh; }}
    .page-header {{ max-width: 1200px; margin: 0 auto 2rem auto; }}
    .page-header h1 {{ font-family: 'Outfit', sans-serif; font-size: 2rem; color: #f1f5f9; margin-bottom: 0.5rem; }}
    .page-header p {{ color: #94a3b8; }}
    .mindmap-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.5rem; max-width: 1400px; margin: 0 auto; }}
    .concept-card {{ background: rgba(30,39,64,0.85); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 1.5rem; transition: all 0.3s ease; }}
    .concept-card:hover {{ border-color: rgba(255,255,255,0.3); transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,0,0,0.4); }}
    .card-header {{ display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }}
    .card-icon {{ width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }}
    .card-title {{ font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 600; color: #f1f5f9; }}
    .card-subtitle {{ font-size: 0.85rem; color: #94a3b8; }}
    .items-list {{ display: flex; flex-direction: column; gap: 0.5rem; }}
    .node-item {{ padding: 0.75rem 1rem; background: rgba(255,255,255,0.03); border-radius: 8px; border-left: 3px solid transparent; transition: all 0.2s ease; }}
    .node-item:hover {{ background: rgba(255,255,255,0.06); }}
    .node-item.warning {{ border-left-color: #ef4444; }}
    .node-item.info {{ border-left-color: #3b82f6; }}
    .node-item.formula {{ border-left-color: #10b981; }}
    .node-item.warning .item-text {{ color: #fca5a5; }}
    .node-item.info .item-text {{ color: #93c5fd; }}
    .node-item.formula .item-text {{ color: #6ee7b7; }}
    .item-text {{ color: #cbd5e1; font-size: 0.9rem; }}
    .item-tip {{ font-size: 0.75rem; color: #64748b; margin-top: 0.25rem; }}
  </style>
</head>
<body>
  <div class="page-header">
    <h1>{icon} Chapter {chapter_num}: {title}</h1>
    <p>South African Litigation Skills - Interactive Study Mind Map</p>
  </div>
  
  <div class="mindmap-grid">
    {cards}
  </div>
</body>
</html>"""

CARD_TEMPLATE = """
    <div class="concept-card">
      <div class="card-header">
        <div class="card-icon" style="background: {color};">
          <span>{card_icon}</span>
        </div>
        <div>
          <div class="card-title">{topic}</div>
          <div class="card-subtitle">{subtitle}</div>
        </div>
      </div>
      <div class="items-list">
        {items}
      </div>
    </div>
"""

ITEM_TEMPLATE = """
        <div class="node-item{item_class}">
          <div class="item-text">&#8226; {topic}</div>
          {tip}
        </div>
"""

def generate_html(chapter_num, data):
    """Generate an interactive HTML mind map for a chapter."""
    
    cards_html = []
    icons = {"people": "&#128101;", "document": "&#128196;", "scales": "&#9878;", "warning": "&#9888;"}
    
    for child in data.get('children', []):
        items_html = []
        for item in child.get('children', []):
            item_class = ""
            if item.get('warning'):
                item_class = " warning"
            elif item.get('info'):
                item_class = " info"
            elif item.get('formula'):
                item_class = " formula"
            
            tip_html = ""
            if item.get('tip'):
                tip_html = f'<div class="item-tip">{item["tip"]}</div>'
            
            items_html.append(ITEM_TEMPLATE.format(
                item_class=item_class,
                topic=item['topic'],
                tip=tip_html
            ))
        
        card_icon = icons.get(child.get('icon', 'document'), "&#128196;")
        cards_html.append(CARD_TEMPLATE.format(
            color=data['color'],
            card_icon=card_icon,
            topic=child['topic'],
            subtitle=child.get('subtitle', ''),
            items=''.join(items_html)
        ))
    
    icon_html = icons.get(data.get('icon', 'document'), "&#128196;")
    return HTML_TEMPLATE.format(
        chapter_num=chapter_num,
        title=data['title'],
        icon=icon_html,
        cards=''.join(cards_html)
    )

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Generating enhanced mind maps...")
    for ch_num, ch_data in CHAPTER_DATA.items():
        html_content = generate_html(ch_num, ch_data)
        output_file = OUTPUT_DIR / f"chapter_{ch_num:02d}_mindmap.html"
        output_file.write_text(html_content, encoding='utf-8')
        print(f"  Created: {output_file.name}")
    
    print("Mind map generation complete!")

if __name__ == "__main__":
    main()
