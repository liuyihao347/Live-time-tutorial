---
name: agent-first-notebook-pdf
description: |
  Generate beautiful, flexible PDF notes using agent-driven markdown content.
  Use when: user explicitly asks to save notes/knowledge to Notebook;
  after quiz/tutorial when user wants to capture key learnings;
  when consolidating research or study materials into a permanent PDF note.
version: 1.1.0
tags: [agent-skill, notebook, pdf, markdown, knowledge-capture, study-notes]
created: 2026-02-23
updated: 2026-02-23
---

# Agent-first Notebook PDF

Two-stage protocol: (1) Agent generates rich markdown content, (2) MCP renders to beautiful PDF.

## When to Use

- User says: "save this to my notebook", "add to notebook", "generate a note"
- After interactive quiz/tutorial when user clicks "Add to Notebook"
- Consolidating scattered knowledge into a structured review document
- Creating quick reference sheets for future review

## Decision Checklist

Before invoking, confirm:
- [ ] User explicitly wants to save/generate a note (not just asking a question)
- [ ] You have enough context to write meaningful content
- [ ] Topic is clear and filename-friendly

## Two-Stage Workflow

### Stage 1: Generate Markdown Content

Think about what makes a good study note:

- **Hook**: Why does this matter? (1-2 sentences)
- **Core concept**: Clear explanation with examples
- **Practical application**: When/how to use it
- **Common pitfalls**: What to watch out for
- **Quick reference**: Checklists, formulas, decision trees

Markdown features supported:
- `# ## ###` headings
- `- ` bullet lists, `1. ` numbered lists
- `> ` blockquotes for tips/warnings
- ` ``` ` fenced code blocks
- Inline `code` for technical terms

### Stage 2: Call save_notebook_note_pdf

```json
{
  "topic": "Binary Search",
  "summary": "O(log n) search for sorted arrays",
  "contentMarkdown": "## When to Use\n- Data is sorted\n- Random access is O(1)\n- Need better than O(n)\n\n## The Pattern\n```python\ndef binary_search(arr, target):\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = lo + (hi - lo) // 2  # Prevent overflow\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1\n```\n\n> Always use `lo + (hi-lo)//2` instead of `(lo+hi)//2` to avoid integer overflow in other languages.",
  "tags": ["algorithm", "search", "interview"],
  "design": { "theme": "clean", "accentColor": "#2563EB" }
}
```

## Design System

| Theme | Accent | Best For |
|-------|--------|----------|
| `clean` | Blue #2563EB | Technical, professional |
| `warm` | Orange #C2410C | Creative, storytelling |
| `forest` | Teal #0F766E | Nature, health, growth |

Override with custom `accentColor` (hex like `#FF5733`) if needed.

## Multi-Scene Examples

### Example 1: Quick Concept Note (Minimal)
```json
{
  "topic": "REST vs GraphQL",
  "summary": "API design trade-offs",
  "contentMarkdown": "## REST\n- Multiple endpoints\n- Fixed response shapes\n- Good for simple CRUD\n\n## GraphQL\n- Single endpoint\n- Client specifies fields\n- Better for complex data graphs",
  "design": { "theme": "clean" }
}
```

### Example 2: Tutorial Capture (With Table)
```json
{
  "topic": "Docker Commands",
  "summary": "Essential commands for container management",
  "contentMarkdown": "## Lifecycle\n\n1. Build image: `docker build -t myapp .`\n2. Run container: `docker run -p 3000:3000 myapp`\n3. Stop: `docker stop <container_id>`",
  "table": {
    "headers": ["Command", "Purpose"],
    "rows": [
      ["docker ps", "List running containers"],
      ["docker images", "List local images"],
      ["docker logs", "View container logs"]
    ]
  },
  "tags": ["docker", "devops", "cheatsheet"],
  "design": { "theme": "forest" }
}
```

### Example 3: Quiz Knowledge Reinforcement
```json
{
  "topic": "CSS Flexbox Alignment",
  "summary": "Common alignment patterns",
  "contentMarkdown": "## Center (Both Axes)\n```css\n.container {\n  display: flex;\n  justify-content: center;\n  align-items: center;\n}\n```\n\n## Common Patterns\n- `justify-content`: main axis (horizontal in row)\n- `align-items`: cross axis (vertical in row)",
  "tags": ["css", "frontend"],
  "design": { "theme": "warm" }
}
```

## Best Practices

1. **Topic naming**: Use 2-5 descriptive words, no special characters
   - ✅ "Binary Search Patterns"
   - ❌ "BS algo #1 (important!!!)"

2. **Summary**: One line, 5-10 words, captures the essence

3. **Content length**: 50-200 words is ideal for review notes

4. **Code blocks**: Always specify language for syntax highlighting

5. **Tables**: Use for comparisons, command references, or data lookup

6. **Tags**: 2-4 tags help with future discovery and filtering

## Error Handling

If PDF generation fails:
- Check if `reportlab` is installed (`pip install reportlab`)
- Verify topic doesn't contain filesystem-special characters
- Ensure table.rows length matches headers count

## Output

- Location: `~/Desktop/Notebook/notes/{topic}.pdf`
- Auto-created folders if don't exist
- File is immediately ready for review/printing
