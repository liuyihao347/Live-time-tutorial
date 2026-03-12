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

<p align="center">
  <img src="Example quiz.png" alt="Quiz GUI Screenshot" width="600">
</p>

---

## 🧠 Highlights

- **Instant Feedback** - Automatically generates quizzes based on task context, with immediate result display, explanation, and walkthrough demo
- **User Feedback Loop** - Type a follow-up prompt at the bottom of the quiz; agent responds and generates another quiz
- **Auto PDF Notebook Generation** - Click "Save to Notebook" to auto-generate PDF with screenshot
- **Easy Integration** - Works with Windsurf, Cursor, Kilo Code, and more

## 🔄 How It Works

```
Task Complete → AI Summarizes → Generate Quiz → User Answers in GUI
→ [Optional: type feedback prompt] → Agent responds → Generate another Quiz (loop)
→ [If Save to Notebook clicked] → PDF Auto-generated → Saved to ~/Desktop/Notebook/
```

## 🚀 Installation

### 1. Build
```bash
npm install
npm run build
```

### 2. Configure IDE
Add to your IDE's MCP config, replacing `[PATH_TO_PROJECT]` with the actual path:

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

### 3. Add global rule (Recommended)
Add this global rule (rules\task-feedback.md) to your agent to increase the trigger frequency of this MCP.

### 4. Restart IDE
Restart your IDE to activate the MCP service.

## 📖 Usage

- **Auto-trigger**: AI asks for a quiz after completing tasks
- **Manual trigger**: Type "give me a quiz" or "quiz" in chat
- **Answer in GUI**: Click an option card to submit instantly
- **Leave feedback** (optional): Type a follow-up prompt in the **Feedback to Agent** box at the bottom
- **PDF auto-generated**: If you clicked Save to Notebook, a PDF will be created automatically

All files are saved directly to `~/Desktop/Notebook/`:
- `{topic}.pdf` - Rich study note with screenshot as header

## 🧰 MCP Tools

### `generate_quiz`

Generate a quiz and open the GUI window. MCP waits for window to close

**Behavior:**
- If user entered **feedback** → Agent responds to feedback, then calls `generate_quiz` again
- If user clicked **Save to Notebook** → Agent automatically calls `save_notebook_note_pdf`
- If user did neither → Agent summarizes and ends conversation

### `set_notebook_path`

Set custom Notebook storage path (default: `~/Desktop/Notebook`).

### `save_notebook_note_pdf`

Generate a rich PDF study note using the `rich-notebook-pdf-generator` agent skill.

## 🎭 Built-in Agent Skills

Located in `src/builtin-skills/rich-notebook-pdf-generator/`:

**SKILL.md** guides the agent to generate content with:

1. **Terminology & Definitions** - Key terms with bold highlighting
2. **Key Concepts & Principles** - Core ideas with critical takeaways
3. **Practical Examples** - Runnable code and real-world scenarios
4. **Analogy & Memory Aids** - Everyday analogies and comparisons
5. **Summary Table** - Comparison tables for quick review
6. **Process Flowchart** - Text-based flowcharts using box-drawing characters

## 📄 License

[MIT](LICENSE)

---

<p align="center">
  Crafted with ❤️ for effective learning
</p>

