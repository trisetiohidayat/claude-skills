---
description: Commit changes to Odoo addon repos, one commit per module
---

You are helping the user commit changes to Odoo custom addon repositories. The project has multiple git folders for different addon types.

## Steps

1. **Find all git folders** in the current working directory and its immediate subdirectories:
   - Run `find . -maxdepth 2 -name ".git" -type d` to find repos
   - Extract the parent folder name for each repo
   - Present each as an option

2. **Ask user which repos to commit** using AskUserQuestion with multiSelect=true:
   - Header: "Select repos"
   - Question: "Which git repos should be committed?"
   - Options should show the repo folder names

3. **For each selected repo**:

   a. Check git status and show what will be committed:
   ```bash
   cd /path/to/repo && git status
   ```
   and `git diff --staged` (if anything staged) or `git diff` (if nothing staged)

   b. **Group files by Odoo module** - Look at the file paths to identify which addon module each changed file belongs to (e.g., `suqma_sale_discount/`, `suqma_pricelist_approval/`, `base_tier_validation/`)

   c. **For each module with changes**:
   - Stage files for that module: `git add module/path/`
   - Show a summary of changes (brief file list with change types)
   - Use AskUserQuestion to select commit type:
      * Header: "Commit type"
      * Question: "What type of change is this for MODULE_NAME?"
      * Options (multiSelect: false):
        - feat: New feature or functionality
        - fix: Bug fix or error correction
        - refactor: Code refactoring (no functional change)
        - docs: Documentation changes only
        - style: Code style/formatting (no logic change)
        - test: Test additions or modifications
        - chore: Build/config/dependency updates
        - perf: Performance improvements
   - Draft commit message automatically using:
     * Format:
       ```
       {type}(module): brief description

       {description}

       - bullet point 1
       - bullet point 2
       ...
       ```
     * Generate description from changed files (e.g., "Add tier validation for sale order discounts")
     * If changes are to XML views: "Add/update views for..."
     * If changes to models: "Add/update model fields and methods for..."
     * If changes to security: "Update access rights for..."
     * If changes to data/demo: "Add/update data records for..."
   - Show drafted commit message and ask for confirmation with AskUserQuestion:
      * Header: "Confirm commit"
      * Question: "Use this commit message for MODULE_NAME?\n\n{type}(module): {description}"
      * Options:
        - Yes, use this message
        - No, I'll provide custom message
   - If user confirms, create commit with footer: `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
   - If user wants custom message, ask via regular user prompt

   d. If there are changes not in any module folder (root-level files like README, config files), ask separately about those as "Root files"

4. **Important rules**:
   - One commit per Odoo module (don't mix modules in one commit)
   - Don't commit files that look like secrets (.env, credentials.json, *.key, *.pem, etc.)
   - Respect `.gitignore` - if files are ignored, don't stage them
   - If nothing to commit in a repo, skip it with a note
   - Show final summary: what repos were processed, how many commits created

5. **Do NOT push** - only create commits locally. Ask user if they want to push after showing summary.

Example output format:
```
## Commit Summary

### suqma-electric (2 commits)
- suqma_sale_discount: Add tier validation for sale order discounts (3 files changed)
- suqma_pricelist_approval: Fix approval workflow state transition (2 files changed)

### suqma-electric-extra (1 commit)
- base_tier_validation: Update documentation (1 file changed)

Total: 3 commits created across 2 repos

Would you like to push to remote? (y/n)
```
