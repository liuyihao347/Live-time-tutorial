---
alwaysApply: true
trigger: always_on
---

# Live-time-tutorial MCP Trigger Rules

## Mandatory Requirement
After completing any user request, if this round of task has formed clear knowledge points, conclusions, repair reasons, implementation steps, or code understanding results, you **must prioritize calling** the `generate_quiz` tool in the `live-time-tutorial` MCP instead of ending the conversation directly.

## Calling Requirements
1. Extract the most valuable knowledge point to consolidate from the content of this round of task.
2. Generate 1 high-quality single-choice question.
3. The `question` must accurately correspond to the conclusion of this round of task.
4. The `options` must provide 4 distinct options.
5. The `correctIndex` must correspond to the only correct answer.
6. The `explanation` must briefly explain why the correct answer is valid.
7. If there are multiple knowledge points, prioritize the most core, universal, and reusable one.
8. If the task is not suitable for generating a question, end normally and briefly state the reason for not generating a question.

## Applicable Scenarios
- All code modification tasks
- All question answering tasks
- All function implementation tasks
- All debugging and troubleshooting tasks

## Prohibited Behaviors
- Directly ending the conversation when a question is suitable to be generated.
- Generating questions unrelated to the current task.
- Generating questions without a basis for the correct answer.