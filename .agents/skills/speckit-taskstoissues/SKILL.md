---
name: "speckit-taskstoissues"
description: "Convert existing tasks into actionable, dependency-ordered GitHub issues for the feature based on available design artifacts."
compatibility: "Requires spec-kit project structure with .specify/ directory"
metadata:
  author: "github-spec-kit"
  source: "templates/commands/taskstoissues.md"
---


## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Repository-Specific Guidance

Before creating issues from tasks in this repository:

- Prefer issue titles and bodies that preserve runtime context: bot, desktop,
  or shared layers.
- Keep explicit contracts, validation expectations, and docs updates visible in
  the issue body when they are part of the task.
- If multiple tiny checklist tasks are obviously part of one coherent change
  slice, prefer a single actionable issue only if the result remains clear and
  traceable to the original tasks.

## Outline

1. Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks` from repo root and parse FEATURE_DIR and AVAILABLE_DOCS list. All paths must be absolute. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").
1. From the executed script, extract the path to **tasks**.
1. Get the Git remote by running:

```bash
git config --get remote.origin.url
```

> [!CAUTION]
> ONLY PROCEED TO NEXT STEPS IF THE REMOTE IS A GITHUB URL

1. For each task in the list, use the GitHub MCP server to create a new issue in the repository that is representative of the Git remote.

   For each issue body, include at minimum:
   - source task ID(s)
   - affected file paths or module area
   - affected runtime(s)
   - required validation
   - required docs/guidance updates, if any

> [!CAUTION]
> UNDER NO CIRCUMSTANCES EVER CREATE ISSUES IN REPOSITORIES THAT DO NOT MATCH THE REMOTE URL
