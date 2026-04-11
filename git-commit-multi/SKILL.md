---
description: Commit changes across multiple git repos with smart grouping
---

You are helping the user commit changes across multiple git repositories in the current project.

## Steps

1. **Find all git folders** in the current working directory and its subdirectories:
   - Run `find . -name ".git" -type d` to find all repos
   - Extract the parent folder name for each repo (the repo root)
   - Present options to the user

2. **Ask user which repos to process** using AskUserQuestion with multiSelect=true:
   - Header: "Select repos"
   - Question: "Which git repos should be committed?"
   - Show repo folder names as options

3. **For each selected repo**:

   a. Check git status:
   ```bash
   cd /path/to/repo && git status
   git diff --stat  # or git diff --staged --stat if staged
   ```

   b. **Smart grouping**: Analyze changed files and group them logically:
   - For Odoo/Python projects: group by module/package
   - For web/JS projects: group by component or feature
   - For general projects: group by directory or file type
   - Root files (README, config, etc.) group separately

   c. **For each logical group**:
   - Show what files will be in this commit
   - Use AskUserQuestion to select commit type:
      * Header: "Commit type"
      * Question: "What type of change is this for GROUP_NAME?"
      * Options (multiSelect: false):
        - feat: New feature or functionality
        - fix: Bug fix or error correction
        - refactor: Code refactoring (no functional change)
        - docs: Documentation changes only
        - style: Code style/formatting (no logic change)
        - test: Test additions or modifications
        - chore: Build/config/dependency updates
        - perf: Performance improvements
   - Draft commit message automatically from changes
   - Show drafted message and ask for confirmation with AskUserQuestion:
      * Header: "Confirm commit"
      * Question: "Use this commit message?\n\n{type}: {description}"
      * Options:
        - Yes, use this message
        - No, I'll provide custom message
   - Stage files: `git add <files>` or `git add <folder>/`
   - Create commit with footer: `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`

   d. Skip files that look like secrets (.env, *.key, credentials, etc.)

4. **Important rules**:
   - One commit per logical group (don't mix unrelated changes)
   - Respect `.gitignore`
   - If nothing to commit in a repo, note it and skip
   - Show summary at the end

5. **Do NOT push** - only create commits. Ask user if they want to push afterward.

Example summary:
```
## Commit Summary

### repo-name (2 commits)
- feature-auth: Add login and OAuth flow (5 files)
- api-users: Add user CRUD endpoints (3 files)

### another-repo (1 commit)
- docs: Update README with setup instructions (1 file)

Total: 3 commits

Push to remote? (y/n)
```
