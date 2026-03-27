# Coding Agent Delivery Checklist

Use this checklist after implementing a change.

## Before editing

- Confirm the user request in one sentence.
- Identify the smallest set of files that likely need changes.
- Check for local instructions, tests, or scripts that affect the task.

## During implementation

- Keep the diff scoped to the request.
- Reuse existing patterns and names from nearby code.
- Avoid speculative abstractions.

## Before finishing

- Run at least one relevant verification command.
- Review the diff for accidental changes.
- Summarize what changed, how it was verified, and any follow-up work.
