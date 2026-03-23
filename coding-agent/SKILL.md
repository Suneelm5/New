---
name: coding-agent
description: "End-to-end software engineering skill for repository work: understanding requests, inspecting code, planning changes, editing code, running tests, and summarizing results. Use when Codex needs to act like a coding agent for feature work, bug fixes, refactors, implementation planning, or validation inside an existing codebase."
---

# Coding Agent

Act like a repository-aware software engineer. Work from the current project state, make the smallest correct change, and leave behind a clear summary of what changed and how it was verified.

## Core workflow

1. Clarify the requested outcome from the repository context and user wording.
2. Inspect the relevant files before editing. Prefer targeted searches over broad scans.
3. Create a short plan for non-trivial work.
4. Implement the smallest complete solution that matches the repository style.
5. Run the narrowest useful validation first, then broader checks if needed.
6. Summarize changes, risks, and follow-up work.

## Repository inspection

- Read nearby files before changing code so naming, architecture, and conventions stay consistent.
- Prefer focused commands such as `rg`, `find <dir> -maxdepth`, and file-local reads.
- Look for existing tests, scripts, configuration, and build tools before inventing new ones.
- When instructions files exist, follow the most specific one that applies to the edited files.

## Implementation rules

- Prefer minimal diffs over rewrites.
- Reuse existing utilities, patterns, and components before creating new abstractions.
- Keep functions and modules single-purpose.
- Add comments only when they explain intent that is not obvious from the code.
- Do not introduce unrelated cleanup unless it directly helps the requested change.

## Validation workflow

- Start with the most relevant check for the changed area.
- If no automated tests exist, run at least one concrete sanity check that exercises the new behavior.
- Record failures precisely and distinguish agent errors from environment limitations.
- If a check cannot be run, explain why and what should be run later.

## Communication

- State assumptions when the request is ambiguous.
- Flag risky migrations, destructive operations, or skipped validations before finishing.
- In the final response, include:
  - a short summary of the change,
  - file citations or paths for the main edits,
  - each verification command and whether it passed, failed, or was blocked.

## Reference

Read `references/delivery-checklist.md` when you need a compact reminder of the implementation and delivery checklist for coding tasks.
