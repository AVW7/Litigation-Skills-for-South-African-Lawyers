---
type: index
tags: [visual-index, study-tools, litigation-skills]
---

# Visual Study Tools Index

This index provides quick access to all visual learning resources for South African Litigation Skills study.

---

## SVG Concept Flowcharts

| Concept | File | Description |
|---------|------|-------------|
| Burden of Proof | `[[Assets/burden_of_proof_visual.svg]]` | Civil vs Criminal standards visualized |
| Pleadings Flow | `[[Assets/pleadings_flow_visual.svg]]` | Document exchange timeline |
| Motion Applications | `[[Assets/motion_application_visual.svg]]` | Affidavit sequence |

---

## Interactive Mind Maps

| Chapter | Topic | Link |
|---------|-------|------|
| 1 | Interviewing Clients & Witnesses | `[[Assets/mindmaps/chapter_01_mindmap.html]]` |
| 5 | Pleadings: Function, Form & Style | `[[Assets/mindmaps/chapter_05_mindmap.html]]` |
| 18 | Cross-Examination | `[[Assets/mindmaps/chapter_18_mindmap.html]]` |

---

## Excalidraw Diagrams

| Diagram | Location | Purpose |
|---------|----------|---------|
| Cross-Exam Workflow | `[[Excalidraw/Cross-Examination-Workflow.excalidraw.md]]` | The duty and techniques |
| Overview Canvas | `[[Litigation-Skills-Overview.canvas]]` | Full course overview |

---

## CSS Theme Files

| Theme | File | Application |
|-------|------|-------------|
| Enhanced Dark Theme | `[[Assets/enhanced-mindmap-theme.css]]` | Apply to all mind maps |

---

## How to Use These Visuals

### In Obsidian
1. Open SVG files directly - they render inline
2. Hover over mind map cards to see details
3. Click links to navigate to related chapters

### In Browser
1. Open `Assets/study-dashboard.html` for full interactive experience
2. Mind maps work standalone in modern browsers
3. SVGs can be printed or embedded

---

## Visual Generation Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| Mind Map Generator | `Assets/generate_mindmaps.py` | Create chapter mind maps |
| Animation Generator | `Assets/animation_generator.py` | Create GIF animations |
| Study Guide Builder | `Assets/build_study_guide.py` | Generate lectures |

---

## Customizing Visuals

### Modify Theme Colors
Edit `Assets/enhanced-mindmap-theme.css`:
```css
:root {
  --bg-primary: #0c1220;     /* Main background */
  --accent-gold: #f59e0b;    /* Primary accent */
  --accent-blue: #3b82f6;    /* Secondary accent */
}
```

### Add New Mind Maps
Edit `Assets/generate_mindmaps.py`:
1. Add chapter data to `CHAPTER_DATA` dictionary
2. Run: `python3 Assets/generate_mindmaps.py`

---

## Study Tips

> [!tip] Visual Learning Strategy
> 1. Start with the `[[Litigation-Skills-Overview.canvas]]` for big picture
> 2. Dive into chapter-specific mind maps for details
> 3. Use SVG flowcharts to memorize procedural sequences
> 4. Quiz yourself by closing notes and redrawing from memory

---

## Related Skills

- [[obsidian-markdown-mastery]] - Markdown syntax guide
- [[obsidian-graph-traversal]] - Navigate linked notes
- [[concept-diagrams]] - Create more diagrams

---

*Last updated: Visual index regenerated with new assets*
