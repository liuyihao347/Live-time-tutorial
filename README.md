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
- **Notebook Export** - Click "Save to Notebook" to capture a screenshot of your quiz result
- **Result Feedback** - After quiz completion, AI receives your answer and asks if you want a detailed study note
- **Skip Anytime** - Decline quizzes without disrupting workflow
- **Easy Integration** - Works with Cursor, Kilo Code, Windsurf & more

## 🔄 How It Works

```
Task Complete → AI Summarizes → Generate Quiz → User Answers in GUI → MCP Returns Result → AI Asks for PDF Note → Generate Rich Content → Save PDF to Notebook
```

1. **Task Trigger** - AI extracts key knowledge points after finishing a task
2. **Quiz Generation** - Creates a multiple-choice question and opens GUI
3. **User Answers** - Click an option in the GUI to submit
4. **Result Captured** - MCP receives your answer, correctness, and explanation
5. **Study Note Prompt** - AI asks if you want a detailed PDF study note
6. **Rich Content Generation** - Creates comprehensive notes with terminology, examples, analogies
7. **PDF Export** - Saves a beautifully formatted note to ~/Desktop/Notebook/notes/

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
- **Save screenshot**: Click **Save to Notebook** after answering to capture result
- **Get study note**: AI will ask if you want a detailed PDF after quiz completion

## 🧰 MCP Tools

- `generate_quiz`: Generate a quiz, open GUI, wait for answer, and return result with system prompt
- `set_notebook_path`: Set custom Notebook path (default: `~/Desktop/Notebook`)
- `save_notebook_note_pdf`: Generate a beautiful PDF study note using agent skills

### Built-in Agent Skills

The MCP includes an agent skill in `src/builtin-skills/`:

**`rich-notebook-pdf-generator`**: Comprehensive study notes with 6 educational sections:
- Terminology Definitions
- Knowledge Network  
- Key Points
- Practical Examples
- Analogies & Comparisons
- Visual Summary

### `generate_quiz` Workflow

When you call `generate_quiz`:
1. GUI window opens with the quiz
2. MCP waits (up to 5 minutes) for you to answer
3. Returns your answer + correctness + explanation
4. Includes system prompt asking if you want a PDF study note
5. If yes → use `rich-notebook-pdf-generator` skill to create content
6. Call `save_notebook_note_pdf` to generate the PDF

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

- `src/index.ts`: MCP service core with quiz generation and PDF export
- `python/quiz_gui.py`: Python GUI for interactive quiz
- `src/builtin-skills/`: Agent skills for PDF content generation

## 📄 License

[MIT](LICENSE)

---

<p align="center">
  Crafted with ❤️ for effective learning
</p>

