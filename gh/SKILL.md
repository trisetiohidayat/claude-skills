---
name: gh
description: GitHub CLI interactions. Use this skill every time the user wants to interact with GitHub or a GitHub repository — creating repos, pushing code, managing visibility, transferring ownership, adding collaborators, creating/deleting issues, PRs, branches, tags, or any git remote operations. Trigger on: "push repo", "create repo", "delete repo", "make it public/private", "transfer to org", "add collaborator", "create branch", "create PR", "delete branch", "gh auth", "github", "repo settings", or any GitHub-related request. ALWAYS use `gh` CLI for GitHub operations — do not manually open URLs unless explicitly asked.
---

# GitHub CLI (`gh`) Skill

## Core Principle

**Always use `gh` CLI for GitHub operations.** Do not manually craft API calls or open browser URLs unless the user explicitly asks to do something that `gh` cannot handle.

Before running any `gh` command:
1. Check `gh auth status` to confirm user is logged in
2. Use `--help` or `gh <command> --help` to confirm correct syntax
3. Report what will happen before doing it for destructive operations (delete, transfer, visibility changes)

---

## Authentication

### Check Auth Status
```bash
gh auth status
```
Shows: logged-in account, active account, token scopes, protocol (https/ssh).

### Switch Active Account
If multiple accounts are logged in (e.g., personal + org):
```bash
gh auth switch -h github.com -u <username>
```

### Refresh Token Scopes
```bash
gh auth refresh -h github.com -s <scope>
```
Common scopes: `repo`, `delete_repo`, `workflow`.

### Re-authenticate
```bash
gh auth login -h github.com
```

---

## Repository Operations

### Check if Repo Exists
```bash
gh repo view <owner>/<repo> [--json field]
```
Exit code 0 = exists, exit code 1 = not found.

### Create Repository

**Personal repo (current user):**
```bash
gh repo create <owner>/<repo> [--private|--public] [--source=<dir>] [--push] [--description "<desc>"]
```

**Transfer to organization:**
```bash
gh repo transfer <owner>/<repo> <target-org>
```

**Important flags:**
- `--private` — only owner/collaborators can see
- `--public` — everyone can see
- `--source=<dir>` — local directory to initialize
- `--push` — push after create (requires commits in source)
- `--clone` — clone after create

### Set Visibility (Public/Private)

```bash
# Change to private
gh repo edit <owner>/<repo> --visibility private --accept-visibility-change-consequences

# Change to public
gh repo edit <owner>/<repo> --visibility public --accept-visibility-change-consequences
```

**Warning:** Moving public → private is irreversible via API for organization repos.

### Delete Repository
```bash
gh repo delete <owner>/<repo> --yes
```
**Requires:** `delete_repo` scope. Use `gh auth refresh -h github.com -s delete_repo` if needed.

### List Repositories
```bash
# List current user's repos
gh repo list [--limit N]

# List org repos
gh repo list <org> [--limit N]
```

### Clone Repository
```bash
gh repo clone <owner>/<repo> [--git-protocol ssh|https]
```

### Sync Fork with Upstream
```bash
gh repo sync <owner>/<fork> --source <upstream-owner>/<upstream-repo>
```

---

## Branch Operations

### Create Branch
```bash
gh repo create-branch <owner>/<repo> --base <base-branch> --name <new-branch>
# OR via git
git checkout -b <branch>
git push -u origin <branch>
```

### List Branches
```bash
gh api repos/<owner>/<repo>/branches
```

### Delete Branch (remote)
```bash
gh repo delete-branch <owner>/<repo> <branch>
# OR via git
git push origin --delete <branch>
```

---

## Collaborator & Access Management

### Add Collaborator (personal repo)
```bash
gh repo collaborator add <username> --repo <owner>/<repo> [--permission read|write|admin]
```

### List Collaborators
```bash
gh repo collaborator list --repo <owner>/<repo>
```

### Remove Collaborator
```bash
gh repo collaborator remove <username> --repo <owner>/<repo>
```

### Add Team to Org Repo (organization repo)
```bash
# Via API (gh CLI doesn't have direct team add command)
gh api -X PUT repos/<org>/<repo>/teams --field name=<team-name>
```

---

## Issues

### Create Issue
```bash
gh issue create --repo <owner>/<repo> --title "<title>" --body "<body>" [--label <labels>] [--assignee <users>]
```

### List Issues
```bash
gh issue list --repo <owner>/<repo> [--state open|closed|all] [--limit N]
```

### View Issue
```bash
gh issue view <number> --repo <owner>/<repo> [--comments]
```

### Close Issue
```bash
gh issue close <number> --repo <owner>/<repo>
```

---

## Pull Requests

### Create PR
```bash
gh pr create --repo <owner>/<repo> --title "<title>" --body "<body>" --base <target-branch> [--label <labels>] [--assignee <users>]
```

### List PRs
```bash
gh pr list --repo <owner>/<repo> [--state open|closed|all] [--limit N]
```

### View PR
```bash
gh pr view <number> --repo <owner>/<repo> [--comments]
```

### Merge PR
```bash
gh pr merge <number> --repo <owner>/<repo> [--admin] [--squash|--merge|--rebase]
```

### Checkout PR locally
```bash
gh pr checkout <number> --repo <owner>/<repo>
```

---

## Git Operations (Remote)

### Set Remote URL (HTTPS → SSH)
```bash
git remote set-url origin git@github.com:<owner>/<repo>.git
```

### Set Remote URL (SSH → HTTPS)
```bash
git remote set-url origin https://github.com/<owner>/<repo>.git
```

### Verify Remote
```bash
git remote -v
```

### Push with Upstream
```bash
git push -u origin <branch>
```

### Check Git Protocol
```bash
gh auth status 2>&1 | grep "Git operations protocol"
```

---

## Workflow: Common Tasks

### Task: Create new repo from local directory (private)
```bash
# 1. Check auth
gh auth status

# 2. Initialize git if needed
git init -b main
git add -A && git commit -m "Initial commit"

# 3. Create repo on GitHub
gh repo create <owner>/<repo> --private --source=. --push --description "<desc>"

# 4. Verify
gh repo view <owner>/<repo>
```

### Task: Make existing repo public
```bash
gh repo edit <owner>/<repo> --visibility public --accept-visibility-change-consequences
gh repo view <owner>/<repo> --json visibility
```

### Task: Transfer repo to organization
```bash
# 1. Verify user is repo owner or org admin
gh repo view <owner>/<repo> --json owner

# 2. Transfer
gh repo transfer <owner>/<repo> <target-org>

# 3. Verify
gh repo view <target-org>/<repo>
```

### Task: Delete a repository
```bash
# 1. Confirm with user first
# 2. Ensure delete_repo scope
gh auth refresh -h github.com -s delete_repo

# 3. Delete
gh repo delete <owner>/<repo> --yes

# 4. Verify
gh repo view <owner>/<repo>  # should fail
```

### Task: Share repo with organization member
```bash
# For personal repo: add as collaborator
gh repo collaborator add <github-username> --repo <owner>/<repo> --permission read

# For org repo: ensure user is org member
gh api orgs/<org>/members/<username>  # 204 = member
```

---

## Output Expectations

Always report after each operation:
- **Success:** repo URL, visibility, key details
- **Failure:** exit code, error message, suggested fix
- **Destructive:** ask user to confirm before executing

Example success output:
```
Done.
Repo    : https://github.com/tri-arkana/portainer-mcp (private)
Branch : main
```

Example confirmation prompt:
```
This will PERMANENTLY delete https://github.com/<owner>/<repo>.
Continue? (yes/no)
```

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `gh: Could not resolve to a Repository` | Repo doesn't exist | Check spelling, or create it first |
| `Must have admin rights to Repository` | No permission | Get admin access or ask owner |
| `Token does not have access` | Missing scope | `gh auth refresh -h github.com -s <scope>` |
| `This API operation needs the "delete_repo" scope` | No delete scope | `gh auth refresh -h github.com -s delete_repo` |
| `--push` enabled but no commits found` | Local repo has no commits | `git add -A && git commit` first |

---

## Useful Flags

- `--json` — Output as JSON for parsing (use `--quiet` to suppress output)
  ```bash
  gh repo view <owner>/<repo> --json visibility,isPrivate,owner --jq '.'
  ```
- `--quiet` — Suppress confirmation prompts (use with caution)
- `--yes` — Auto-confirm destructive actions
- `-F, --field` — Filter JSON output fields
