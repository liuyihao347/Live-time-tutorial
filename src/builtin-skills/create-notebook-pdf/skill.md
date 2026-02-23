---
name: agent-first-notebook-pdf
description: |
  Complete agent-driven PDF note generation workflow with knowledge expansion,
  demonstration analysis, and memory techniques.
  Use when: user says "generate notebook PDF" or "create PDF for this quiz";
  after user clicked "Add to Notebook" in quiz GUI;
  when user wants comprehensive knowledge capture from quiz results.
version: 2.1.0
tags: [agent-skill, notebook, pdf, knowledge-graph, study-notes, memory-techniques]
created: 2026-02-23
updated: 2026-02-23
---

# Agent-first Notebook PDF (Complete Workflow)

## Overview

When user clicks "Add to Notebook" in the quiz GUI, the GUI saves quiz data to a pending file. The agent then executes this multi-stage knowledge capture process:

1. **Get Pending Quiz** - Read quiz data saved by GUI
2. **Knowledge Expansion** - Expand terminology and build knowledge network
3. **Demonstration Analysis** - Generate step-by-step process walkthrough
4. **Memory Techniques** - Create analogies and memory aids
5. **Generate PDF** - Call `save_notebook_note_pdf` with rich content

## Trigger Conditions

- User says: "generate notebook PDF", "create PDF for this quiz", "save to notebook"
- User has clicked "Add to Notebook" in the quiz GUI
- User wants comprehensive knowledge capture from a quiz

## Complete Workflow

### Stage 1: Get Pending Quiz

First, call the MCP tool to get the quiz data saved by GUI:

```
Call: get_pending_quiz (no arguments needed)
```

This returns:
```json
{
  "quiz": {
    "question": "What is the time complexity of binary search?",
    "options": ["O(1)", "O(log n)", "O(n)", "O(n^2)"],
    "correctIndex": 1,
    "explanation": "Binary search halves the search space...",
    "knowledgeSummary": "Divide and conquer|Logarithmic time|Sorted data",
    "category": "Algorithm"
  },
  "selectedIndex": 1,
  "isCorrect": true,
  "timestamp": "2026-02-23T18:30:00"
}
```

### Stage 2: Knowledge Expansion (Agent-Driven)

Analyze the quiz content and expand into a knowledge network:

**What to generate:**

1. **Core Terminology**
   - Define key terms from the question
   - Explain related concepts
   - Link to prerequisite knowledge

2. **Knowledge Network**
   - What concepts are related?
   - What are the prerequisites?
   - What advanced topics build on this?

3. **Practical Applications**
   - Where is this used in real-world?
   - Common use cases
   - When NOT to use it

**Example expansion for "Binary Search":**
```
Core Terminology:
- Binary Search: A divide-and-conquer algorithm that finds an element in O(log n)
- Time Complexity O(log n): Operations grow logarithmically with input size
- Sorted Array: Prerequisite data structure for binary search

Knowledge Network:
├── Prerequisites
│   ├── Arrays (random access O(1))
│   ├── Sorting algorithms
│   └── Big O notation
├── Related Concepts
│   ├── Ternary search (O(log₃ n))
│   ├── Exponential search
│   └── Interpolation search
└── Advanced Topics
    ├── Binary search trees
    ├── Balanced trees (AVL, Red-Black)
    └── Database indexing (B-trees)
```

### Stage 3: Demonstration Analysis (Agent-Driven)

Create a step-by-step walkthrough that shows HOW to think through similar problems:

**Structure:**

1. **Problem Decomposition**
   - What is the question really asking?
   - What constraints/conditions matter?

2. **Solution Walkthrough**
   - Step-by-step reasoning process
   - Why each step is necessary
   - Common decision points

3. **Example Trace**
   - Concrete example with actual values
   - Show the algorithm in action

**Example for Binary Search:**
```
Problem Decomposition:
- Question asks for time complexity → analyze algorithm behavior
- Binary search = repeatedly halve search space
- Each iteration: O(1) work, halves remaining elements

Solution Walkthrough:
Step 1: Identify the algorithm pattern
        → "Binary" in name suggests divide-in-half approach
Step 2: Count iterations needed
        → n → n/2 → n/4 → ... → 1
        → How many times can we divide n by 2?
        → log₂(n) times
Step 3: Work per iteration
        → Compare middle element, adjust bounds
        → Constant time O(1)
Step 4: Total complexity
        → iterations × work per iteration
        → log₂(n) × O(1) = O(log n)

Example Trace:
Array: [1, 3, 5, 7, 9, 11, 13, 15]  (n=8)
Target: 11

Iteration 1: mid=7 (value 9), 11 > 9, search right half
             [9, 11, 13, 15]
Iteration 2: mid=11 (value 11), found!
             Total: 2 iterations = log₂(8) = 3 (worst case)
```

### Stage 4: Memory Techniques (Agent-Driven)

Create memorable analogies and memory aids:

**Types of memory aids:**

1. **Analogies** - Connect to familiar concepts
2. **Visualizations** - Mental images
3. **Mnemonics** - Catchy phrases
4. **Contrast Tables** - Compare with alternatives

**Example for Binary Search:**
```
Analogy:
"Binary search is like finding a word in a dictionary:
 You don't check every page from A to Z.
 You open to the middle, see if you're before or after,
 then eliminate half the dictionary in one move."

Memory Trick:
"Binary = 2 choices (left or right)
 Each step cuts the problem in HALF
 Like folding a paper repeatedly until tiny"

Contrast Table:
| Algorithm      | Time      | Requirement    |
|----------------|-----------|----------------|
| Linear Search  | O(n)      | None           |
| Binary Search  | O(log n)  | Sorted         |
| Hash Lookup    | O(1)      | Hash table     |

When to use: "Sorted data + Need speed = Binary search"
```

### Stage 5: Generate PDF

After generating all content, call `save_notebook_note_pdf`:

```json
{
  "topic": "Binary Search Time Complexity",
  "summary": "O(log n) search algorithm for sorted arrays",
  "contentMarkdown": "
# Knowledge Expansion

## Core Terminology

**Binary Search**: A divide-and-conquer algorithm...

**Time Complexity O(log n)**: Operations grow logarithmically...

## Knowledge Network

├── Prerequisites: Arrays, Sorting, Big O
├── Related: Ternary search, Exponential search
└── Advanced: BST, Balanced trees, B-trees

# Demonstration Analysis

## Solution Walkthrough

Step 1: Identify pattern → divide-in-half
Step 2: Count iterations → log₂(n)
...

## Example Trace

Array: [1,3,5,7,9,11,13,15], Target: 11
Iteration 1: mid=9, 11>9, go right
Iteration 2: mid=11, found!

# Memory Techniques

## Analogy

\"Like finding a word in a dictionary...\"

## Quick Formula

Sorted + Speed → Binary Search
",
  "tags": ["algorithm", "search", "complexity", "interview"],
  "design": { "theme": "clean", "accentColor": "#3B82F6" }
}
```

## Quick Start Example

When user says "generate notebook PDF":

```
1. Call get_pending_quiz
2. Analyze the quiz data
3. Generate knowledge expansion content
4. Generate demonstration analysis
5. Generate memory techniques
6. Call save_notebook_note_pdf with all content
7. Report success to user
```

## Best Practices

1. **Depth Over Breadth** - Go deep on key concepts rather than shallow on many
2. **Concrete Examples** - Every abstract concept needs a concrete example
3. **Actionable Memory Aids** - Mnemonics should be immediately useful
4. **Cross-References** - Link to related topics for future exploration
5. **User's Answer Context** - Acknowledge whether user answered correctly

## Error Handling

- If `get_pending_quiz` returns error: Tell user to click "Add to Notebook" in GUI first
- If knowledge expansion is too long: Prioritize most relevant concepts
- If quiz data incomplete: Generate content based on available information

## Dependencies

- MCP tool: `get_pending_quiz` - Get quiz data from GUI
- MCP tool: `save_notebook_note_pdf` - Generate the final PDF
- Python with reportlab (for PDF rendering)
