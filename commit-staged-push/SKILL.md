---
name: commit-staged-push
description: >
  Git workflow skill for committing staged changes and pushing to remote.
  Trigger when user says "commit staged", "commit and push", "git commit push",
  or any variation asking to commit and push staged changes. This skill ensures
  proper commit message format, asks for user confirmation of git config
  (name and email), and does NOT include Co-Authored-By in commits unless
  explicitly requested. Automatically generates commit message from staged changes.
---

# Commit Staged and Push

This skill handles git commit and push workflow with proper user confirmation.

## Workflow

### Step 1: Check Git Status
Always check `git status` first to see staged vs unstaged changes.

### Step 2: Check Git Config
Run these commands to get current git user config:
```bash
git config user.name
git config user.email
```

### Step 3: Ask User Confirmation
Ask user if the name and email are correct. If wrong, ask for the correct values and update:
```bash
git config user.name "Correct Name"
git config user.email "correct@email.com"
```

### Step 4: Show Staged Changes
Run `git diff --cached` to show what will be committed. Present this to user for confirmation.

### Step 5: Generate Commit Message (Auto-Summarize)
**DO NOT ask user for commit message.** Instead, analyze the staged changes and generate a commit message automatically:

- Read `git diff --cached` output
- Identify what files changed and their purpose
- Summarize into a commit message following the format below
- Present the proposed commit message to user for confirmation
- If user wants to change, ask for their preferred message

### Step 6: Commit and Push
After user confirms commit message, run:
```bash
git commit -m "message"
git push
```

## Commit Message Format

**Generate from changes, DO NOT ask user.**

```
[TYPE] short description

- Detailed bullet points (if needed)
```

Types:
- `[FIX]` - Bug fixes
- `[ADD]` - New features
- `[UPDATE]` - Updates to existing features
- `[REFACTOR]` - Code refactoring
- `[DOCS]` - Documentation changes
- `[TEST]` - Test changes
- `[PERF]` - Performance improvements

**DO NOT add Co-Authored-By line unless explicitly requested by user.**

## Important Notes

1. **Always show staged diff before committing** - user needs to see what they're committing
2. **Generate commit message from changes** - analyze staged files and propose appropriate message
3. **Verify git config before committing** - prevent wrong author on commits
4. **No Co-Authored-By by default** - this is intentional, only add if requested
5. **Show result after push** - confirm success with commit hash
