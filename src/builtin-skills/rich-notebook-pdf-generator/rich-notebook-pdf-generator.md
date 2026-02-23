---
name: rich-notebook-pdf-generator
description: |
  Generate comprehensive PDF study notes with rich educational content sections.
  Use when: user completes a quiz and wants a detailed study note; 
  when consolidating knowledge into a structured review document with multiple learning perspectives.
version: 1.0.0
tags: [agent-skill, notebook, pdf, study-notes, knowledge-consolidation, educational-content]
created: 2026-02-23
updated: 2026-02-23
---

# Rich Notebook PDF Generator

Generate comprehensive study notes with 6 educational content sections.

## When to Use

- After quiz completion when user wants detailed study materials
- When user says: "create a study note", "save this as PDF", "make a learning guide"
- When consolidating scattered concepts into structured knowledge

## Content Structure Template

Generate contentMarkdown with these 6 sections:

### 1. Terminology Definitions
Explain key terms clearly:
- Define each term in simple language
- Include formulas if applicable
- Use inline `code` for technical terms

### 2. Knowledge Network
Connect to related concepts:
- Prerequisites (what to know first)
- Related topics (what connects to this)
- Follow-up concepts (where this leads)

### 3. Key Points
Critical takeaways:
- Must-remember facts
- Common misconceptions to avoid
- Decision criteria (when to use this)

### 4. Practical Examples
Code or scenario examples:
- Minimal working example
- Real-world application scenario
- Step-by-step walkthrough

### 5. Analogies & Comparisons
Helpful learning aids:
- Everyday analogies
- Comparison with similar concepts
- Pros/cons tradeoffs

### 6. Visual Summary
Tables, checklists, or diagrams:
- Decision flowchart
- Comparison table
- Quick reference checklist

## Example Payload

```json
{
  "topic": "Binary Search Algorithm",
  "summary": "O(log n) search technique for sorted data",
  "contentMarkdown": "## 1. Terminology Definitions\n\n**Binary Search**: A divide-and-conquer algorithm that repeatedly divides the search interval in half.\n\n**Time Complexity**: O(log n) - logarithmic time means the work grows slowly even as data increases.\n\n**Search Space**: The current range of indices being examined (initially the entire array).\n\n## 2. Knowledge Network\n\n**Prerequisites**: Arrays, sorting, time complexity basics\n\n**Related Topics**: Linear search, interpolation search, exponential search\n\n**Applications**: Database indexing, dictionary lookup, version control bisecting\n\n## 3. Key Points\n\n- Data must be sorted before applying binary search\n- Always calculate mid as `low + (high - low) / 2` to prevent overflow\n- Binary search works on any sorted sequence (arrays, lists with random access)\n- Iterative version is preferred over recursive for space efficiency\n\n## 4. Practical Examples\n\n```python\ndef binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    \n    while low <= high:\n        mid = low + (high - low) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    \n    return -1  # Not found\n```\n\n**Use case**: Finding a word in a 100,000-word dictionary. Linear search: up to 100,000 steps. Binary search: at most 17 steps.\n\n## 5. Analogies & Comparisons\n\n**Analogy**: Finding a word in a dictionary. You don't start at page 1; you flip to the middle, then decide to go forward or back.\n\n**vs Linear Search**: Binary is faster but requires sorted data. Linear works on unsorted but is O(n).\n\n**vs Hash Table**: Hash lookup is O(1) but needs extra space. Binary is in-place with O(log n).\n\n## 6. Visual Summary\n\n| Scenario | Algorithm | Time | Space |\n|----------|-----------|------|-------|\n| Sorted array, frequent searches | Binary Search | O(log n) | O(1) |\n| Unsorted data | Linear Search | O(n) | O(1) |\n| Frequent lookups, memory OK | Hash Table | O(1) avg | O(n) |\n\n**Decision Flowchart**:\n1. Is data sorted? → No: Sort first or use Linear/Hash\n2. Need in-place? → No: Consider Hash Table\n3. Use Binary Search",
  "tags": ["algorithm", "search", "interview"],
  "design": { "theme": "clean", "accentColor": "#2563EB" }
}
```

## Best Practices

1. **Start with the big picture**: Why does this matter?
2. **Use consistent formatting**: `code` for code, **bold** for key terms
3. **Keep examples runnable**: Provide complete, copy-paste ready code
4. **Make analogies relatable**: Use everyday experiences
5. **Visual tables first**: Most learners prefer tables over long text

## Output

- Saved to: `~/Desktop/Notebook/notes/{topic}.pdf`
- Uses `save_notebook_note_pdf` MCP tool
- Default theme: `clean` with blue accent

Dependencies: Python with reportlab (auto-checked by MCP)
