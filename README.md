# South African Litigation Skills & Knowledge Graph

This workspace is a structured study and reference environment based on Chris Marnewick SC's *Litigation Skills for South African Lawyers*. It contains an interlinked Obsidian vault, a web-based interactive case dashboard, a Graphify-generated knowledge graph database, and custom automation scripts.

---

## 📂 Project Structure

- **[vault/](file:///Users/ajadvanwyk/Downloads/Litigation%20Skills%20for%20South%20African%20Lawyers.pdf/vault/)**: An Obsidian study vault featuring:
  - **Walkthrough lectures** (`vault/Lectures/`): Step-by-step guides for all 29 chapters of the textbook.
  - **Legal tests & formulas** (`vault/Formulas/`): Structured, formal tests for topics like Negligence, Urgent Applications, and Spoliation.
  - **Terminology index** (`vault/Terms/`): Key litigation terms with definitions, analogies, and visual diagrams.
  - **MOC indexes** (`vault/Indexes/` & `Home.md`): Central maps of all notes.
- **[dashboard/](file:///Users/ajadvanwyk/Downloads/Litigation%20Skills%20for%20South%20African%20Lawyers.pdf/dashboard/)**: A web application built with React and Vite. It serves as a visual client mindmap, trial timeline, and interactive case explorer.
- **[graphify-out/](file:///Users/ajadvanwyk/Downloads/Litigation%20Skills%20for%20South%20African%20Lawyers.pdf/graphify-out/)**: The compiled knowledge graph output, including:
  - `graph.json`: The compiled NetworkX-compatible JSON graph.
  - `graph.html`: An interactive, browser-based 3D visualization of the graph structure.
  - `GRAPH_REPORT.md`: A plain-language audit report listing "god nodes", community clusters, and surprising connections.
- **[scripts/](file:///Users/ajadvanwyk/Downloads/Litigation%20Skills%20for%20South%20African%20Lawyers.pdf/scripts/)**: Python automation utilities for markdown linting, AST extraction, parallel LLM processing, and vault assembly.
- **[AGENTS.md](file:///Users/ajadvanwyk/Downloads/Litigation%20Skills%20for%20South%20African%20Lawyers.pdf/AGENTS.md)**: The South African Litigation Skills & Etiquette Context Guide. This document defines the protocol and ethical boundaries that must be strictly followed by all coding agents or practitioners working in this repository.

---

## 🚀 Getting Started

### 1. Exploring the Obsidian Vault
1. Open the [Obsidian](https://obsidian.md) application.
2. Select **Open folder as vault** and choose the `vault/` directory in this folder.
3. Open `Home.md` or `Indexes/All Lectures.md` to begin browsing.
4. Enable standard page previews to hover-link notes. The Dataview plugin is recommended to power dynamic table views.

### 2. Running the Case Dashboard
Start the Vite development server to view the interactive dashboard:
```bash
cd dashboard
npm install
npm run dev
```
Open the printed URL (typically `http://localhost:5173`) in your web browser.

### 3. Querying the Knowledge Graph
The Graphify knowledge graph enables intelligent traversal of relationships, concepts, and dependencies across the book. You can query it directly using the CLI:
* **Shortest Path between concepts:**
  ```bash
  graphify path "Cause of Action" "Pleadings"
  ```
* **Node Explanations:**
  ```bash
  graphify explain "Facta Probanda"
  ```
* **Interactive BFS Search:**
  ```bash
  graphify query "What are the requirements for an urgent application?"
  ```

---

## 🏛️ Litigation Protocol & Etiquette Summary

All practitioners and agents in this workspace must adhere to the professional conduct guidelines defined in [AGENTS.md](file:///Users/ajadvanwyk/Downloads/Litigation%20Skills%20for%20South%20African%20Lawyers.pdf/AGENTS.md):
1. **Duty to the Court takes precedence:** Counsel has a primary obligation to assist the court and never mislead on facts or law.
2. **Courtroom Etiquette:** Use correct modes of address ("My Lord"/"My Lady" in the High Court; "Your Worship" in the Magistrates' Court) and robe correctly when appearing.
3. **Pleadings Drafting:** Plead only the *facta probanda* (material facts), not the *facta probantia* (evidence). Every claim must conclude with a clear prayer for relief.
4. **Trial Conduct:** Perform examination-in-chief chronologically without leading on disputed facts. Always "put your version" to opposing witnesses during cross-examination on contested points.

---

## 📖 Content & Copyright

The content and notes in this repository are derived from Chris Marnewick SC's *Litigation Skills for South African Lawyers*. The underlying legal theory, structure, and text remain the copyright of the original author.
