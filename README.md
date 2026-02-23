<p align="center">
  <img src="https://img.shields.io/badge/MCP-Compatible-6366f1?style=flat-square" alt="MCP Compatible">
  <img src="https://img.shields.io/badge/Cursor-Supported-10b981?style=flat-square" alt="Cursor Supported">
  <img src="https://img.shields.io/badge/Kilo_Code-Supported-10b981?style=flat-square" alt="Kilo Code Supported">
  <img src="https://img.shields.io/badge/Windsurf-Supported-10b981?style=flat-square" alt="Windsurf Supported">
  <img src="https://img.shields.io/badge/License-MIT-f59e0b?style=flat-square" alt="MIT License">
</p>

<h1 align="center">⚡ Live-time-tutorial MCP</h1>

<p align="center">
  <a href="README.md">English</a> | <a href="README_CN.md">Chinese</a>
</p>

<p align="center">
  <strong>AI generates interactive knowledge quizzes with instant feedback and one-click Notebook export</strong>
</p>

---

## 🧠 Highlights

- **Polished GUI** - Modern Python quiz interface with card-style options
- **One-click Submit** - Click any option to submit instantly (no extra submit step)
- **Instant Feedback** - Clear result status, explanation, and walkthrough demo
- **Notebook Export** - One-click “Add to My Notebook” saves a styled PDF note
- **Skip Anytime** - Decline quizzes without disrupting workflow
- **Easy Integration** - Works with Cursor, Kilo Code, Windsurf & more

## 🔄 How It Works

```
Task Complete → AI Summarizes → Quiz Prompt → Generate Quiz → One-click Answer → Instant Feedback → Save to Notebook
```

1. **Task Trigger** - AI extracts key knowledge points after finishing a task
2. **Optional Quiz** - Asks if you want a quiz to reinforce memory
3. **On-the-fly Generation** - Creates a multiple-choice question instantly
4. **Smart Evaluation** - Instantly checks correctness after one click
5. **Knowledge Reinforcement** - Shows explanation + walkthrough + key points
6. **Notebook Capture** - Exports a polished PDF note with sections, table, and chart

## 🚀 Installation

### 1. Build
```bash
npm install
npm run build
```

### 2. Configure IDE
Add to your IDE's MCP config, replacing `[PATH_TO_PROJECT]` with the actual path:

**Config locations:**
- **Cursor**: `.cursor/mcp.json`
- **Windsurf**: `.windsurf/mcp.json`
- **VS Code / Kilo Code**: `.vscode/mcp.json`

**Configuration:**
```json
{
  "mcpServers": {
    "live-time-tutorial": {
      "command": "node",
      "args": ["[PATH_TO_PROJECT]/dist/index.js"],
      "env": { "NODE_ENV": "production" },
      "autoApprove": ["generate_quiz", "set_notebook_path", "save_notebook_note_pdf"]
    }
  }
}
```

### 3. Restart IDE
Restart your IDE to activate the MCP service.

## 📖 Usage

- **Auto-trigger**: AI asks for a quiz after completing tasks
- **Manual trigger**: Type "give me a quiz" or "quiz" in chat
- **Answer in GUI**: Click an option card to submit instantly
- **Save note**: Click **Add to My Notebook (PDF)** after answering

## 🧰 MCP Tools

- `generate_quiz`: Generate a quiz and open the Live-time-tutorial GUI
- `set_notebook_path`: Set custom Notebook path (default: `~/Desktop/Notebook`)
- `save_notebook_note_pdf`: Built-in LLM/agent-skill driven Notebook PDF generation

### `save_notebook_note_pdf` (Agent-skill Friendly)

Use your agent skills to generate rich markdown first, then pass it via `contentMarkdown`.
This avoids rigid templates and gives flexible structure and styling.

- Preferred flexible input: `contentMarkdown`
- Optional structured input: `sections`, `keyPoints`, `table`, `chart`
- Optional style input: `design.theme` (`clean` / `warm` / `forest`), `design.accentColor`

Minimal example payload:

```json
{
  "topic": "Binary Search Decision Strategy",
  "summary": "Fast review note",
  "contentMarkdown": "# Core Idea\nBinary search halves search space each step.\n\n## Checklist\n- Sorted data required\n- Use low/high boundaries\n- Prevent overflow in mid\n\n> Prefer binary search when random access is O(1)",
  "tags": ["algorithm", "search"],
  "design": {
    "theme": "clean",
    "accentColor": "#2563EB"
  }
}
```

## 🏗️ Project Structure

- `src/index.ts`: MCP service core
- `vscode-extension/`: VS Code helper extension

## 📄 License

[MIT](LICENSE)

---

<p align="center">
  Crafted with ❤️ for effective learning
</p>

