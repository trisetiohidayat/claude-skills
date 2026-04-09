---
name: cmux-control
description: |
  Control cmux terminal multiplexer via Unix socket. Use this skill whenever the user wants to:
  - Manage windows, workspaces, panes, or surfaces in cmux
  - Send commands or keystrokes to terminal panes
  - Open new terminal splits or browser panels
  - Control browser automation within cmux
  - Read screen content from cmux terminals
  - Send notifications or manage sidebar status
  - Any cmux-related operations (new-window, new-split, send, focus-pane, etc.)

  This skill covers the full cmux CLI with all commands for window/workspace/pane/surface management,
  terminal interaction, browser control, and tmux compatibility.
compatibility: Requires cmux to be installed and running
---

# cmux Control Skill

This skill provides comprehensive control over cmux (a terminal multiplexer) via its CLI. cmux communicates via Unix socket.

## Basic Usage

All cmux commands use the syntax: `cmux [options] <command> [arguments]`

### Handling References

cmux accepts multiple reference formats:
- **UUIDs**: Full UUID format
- **Short refs**: `window:1/workspace:2/pane:3/surface:4`
- **Indexes**: Numeric indices (0-based)
- **Names**: Workspace/window names

For `tab-action`, you can also use `tab:<n>`.

---

## Command Categories

### 1. Information Commands

```bash
# Get cmux version
cmux version

# Show welcome message
cmux welcome

# Show keyboard shortcuts
cmux shortcuts

# Check if cmux is running
cmux ping

# Get cmux capabilities
cmux capabilities

# Get current workspace/surface info
cmux identify
cmux identify --workspace <id|ref|index>
cmux identify --surface <id|ref|index>
cmux identify --no-caller
```

---

### 2. Window Management

```bash
# List all windows
cmux list-windows

# Get current window
cmux current-window

# Create new window
cmux new-window

# Focus a window
cmux focus-window --window <id|ref>

# Close a window
cmux close-window --window <id|ref>

# Move workspace to window
cmux move-workspace-to-window --workspace <id|ref> --window <id|ref>

# Reorder workspace within window
cmux reorder-workspace --workspace <id|ref|index> \
  --index <n> \
  --window <id|ref|index>

# Alternative ordering
cmux reorder-workspace --workspace <id|ref|index> \
  --before <id|ref|index> \
  --window <id|ref|index>

cmux reorder-workspace --workspace <id|ref|index> \
  --after <id|ref|index> \
  --window <id|ref|index>

# Window actions (attach, detach, etc.)
cmux workspace-action --action <name> [--workspace <id|ref|index>] [--title <text>]

# Rename window
cmux rename-window [--workspace <id|ref|index>] <title>

# Navigation
cmux next-window
cmux previous-window
cmux last-window
```

---

### 3. Workspace Management

```bash
# List all workspaces
cmux list-workspaces

# Get current workspace
cmux current-workspace

# Create new workspace
cmux new-workspace
cmux new-workspace --cwd <path>
cmux new-workspace --command <text>

# Select workspace
cmux select-workspace --workspace <id|ref>

# Close workspace
cmux close-workspace --workspace <id|ref>

# Rename workspace
cmux rename-workspace [--workspace <id|ref|index>] <title>
```

---

### 4. Pane Management

```bash
# List panes in workspace
cmux list-panes [--workspace <id|ref>]

# Create new split (terminal pane)
cmux new-split left --workspace <id|ref>
cmux new-split right --workspace <id|ref>
cmux new-split up --workspace <id|ref>
cmux new-split down --workspace <id|ref>

# Split at specific surface/panel
cmux new-split left --surface <id|ref> --panel <id|ref>

# Focus pane
cmux focus-pane --pane <id|ref> [--workspace <id|ref>]

# Create new pane
cmux new-pane --type terminal --direction left
cmux new-pane --type browser --direction right --url <url>
cmux new-pane --type terminal --workspace <id|ref>

# List panels
cmux list-panels [--workspace <id|ref>]

# Focus panel
cmux focus-panel --panel <id|ref> [--workspace <id|ref>]

# Resize pane (tmux compatibility)
cmux resize-pane --pane <id|ref> -L
cmux resize-pane --pane <id|ref> -R
cmux resize-pane --pane <id|ref> -U
cmux resize-pane --pane <id|ref> -D --amount <n>

# Swap pane
cmux swap-pane --pane <id|ref> --target-pane <id|ref>

# Break pane to new window
cmux break-pane [--workspace <id|ref>] [--pane <id|ref>] [--surface <id|ref>] [--no-focus]

# Join pane to another
cmux join-pane --target-pane <id|ref> [--workspace <id|ref>] [--pane <id|ref>] [--surface <id|ref>] [--no-focus]

# Last pane
cmux last-pane [--workspace <id|ref>]
```

---

### 5. Surface Management

Surfaces are individual terminal or browser instances within panes.

```bash
# List pane surfaces
cmux list-pane-surfaces [--workspace <id|ref>] [--pane <id|ref>]

# Create new surface (terminal or browser)
cmux new-surface --type terminal --pane <id|ref> --workspace <id|ref>
cmux new-surface --type browser --pane <id|ref> --url <url>

# Close surface
cmux close-surface --surface <id|ref> [--workspace <id|ref>]

# Move surface between panes/windows
cmux move-surface --surface <id|ref|index> --pane <id|ref|index>
cmux move-surface --surface <id|ref|index> --before <id|ref|index>
cmux move-surface --surface <id|ref|index> --after <id|ref|index>
cmux move-surface --surface <id|ref|index> --index <n>
cmux move-surface --surface <id|ref|index> --focus true

# Reorder surface
cmux reorder-surface --surface <id|ref|index> --index <n>
cmux reorder-surface --surface <id|ref|index> --before <id|ref|index>
cmux reorder-surface --surface <id|ref|index> --after <id|ref|index>

# Tab actions
cmux tab-action --action <name> [--tab <id|ref|index>] [--surface <id|ref|index>] [--workspace <id|ref|index>] [--title <text>] [--url <url>]

# Rename tab
cmux rename-tab [--workspace <id|ref>] [--tab <id|ref>] [--surface <id|ref>] <title>

# Drag surface to split
cmux drag-surface-to-split --surface <id|ref> left
cmux drag-surface-to-split --surface <id|ref> right
cmux drag-surface-to-split --surface <id|ref> up
cmux drag-surface-to-split --surface <id|ref> down

# Refresh surfaces
cmux refresh-surfaces

# Surface health check
cmux surface-health [--workspace <id|ref>]

# Trigger flash notification
cmux trigger-flash [--workspace <id|ref>] [--surface <id|ref>]
```

---

### 6. Tree View

```bash
# Show workspace tree
cmux tree

# Show tree for specific workspace
cmux tree --workspace <id|ref|index>

# Show all workspaces
cmux tree --all
```

---

### 7. Terminal Interaction

```bash
# Read screen content
cmux read-screen [--workspace <id|ref>] [--surface <id|ref>] [--scrollback] [--lines <n>]

# Send text to surface
cmux send --workspace <id|ref> --surface <id|ref> <text>
# Example: Send "ls -la" and Enter
cmux send --surface <id|ref> "ls -la"

# Send key to surface
cmux send-key --workspace <id|ref> --surface <id|ref> <key>
# Example: Send Enter key
cmux send-key --surface <id|ref> "Enter"

# Send to panel
cmux send-panel --panel <id|ref> [--workspace <id|ref>] <text>

# Send key to panel
cmux send-key-panel --panel <id|ref> [--workspace <id|ref>] <key>

# Clear history
cmux clear-history [--workspace <id|ref>] [--surface <id|ref>]

# Capture pane (tmux compatibility)
cmux capture-pane [--workspace <id|ref>] [--surface <id|ref>] [--scrollback] [--lines <n>]

# Respawn pane with new command
cmux respawn-pane [--workspace <id|ref>] [--surface <id|ref>] --command <cmd>
```

---

### 8. Notifications

```bash
# Send notification
cmux notify --title <text> [--subtitle <text>] [--body <text>] \
  [--workspace <id|ref>] [--surface <id|ref>]

# List notifications
cmux list-notifications

# Clear all notifications
cmux clear-notifications
```

---

### 9. Sidebar/Status Management

```bash
# Set status key-value
cmux set-status <key> <value> [--icon <name>] [--color #hex] [--workspace <id|ref>]

# Clear status key
cmux clear-status <key> [--workspace <id|ref>]

# List status
cmux list-status [--workspace <id|ref>]

# Set progress bar
cmux set-progress <0.0-1.0> [--label <text>] [--workspace <id|ref>]

# Clear progress
cmux clear-progress [--workspace <id|ref>]

# Write to log
cmux log --level <debug|info|warn|error> [--source <name>] [--workspace <id|ref>] -- <message>

# Clear log
cmux clear-log [--workspace <id|ref>]

# List log entries
cmux list-log [--limit <n>] [--workspace <id|ref>]

# Sidebar state
cmux sidebar-state [--workspace <id|ref>]
```

---

### 10. Browser Control

cmux includes an embedded browser with automation capabilities.

```bash
# Open URL in browser surface
cmux browser open https://example.com
cmux browser open-split https://example.com

# Navigate to URL
cmux browser goto <url>
cmux browser navigate <url> [--snapshot-after]

# Browser navigation
cmux browser back
cmux browser forward
cmux browser reload [--snapshot-after]

# Get current URL
cmux browser url
cmux browser get-url

# Take snapshot
cmux browser snapshot
cmux browser snapshot --interactive
cmux browser snapshot --cursor
cmux browser snapshot --compact
cmux browser snapshot --max-depth <n>
cmux browser screenshot --out <path>
cmux browser screenshot --json

# Wait for element
cmux browser wait --selector <css>
cmux browser wait --text <text>
cmux browser wait --url-contains <text>
cmux browser wait --load-state complete
cmux browser wait --function <js>

# Click elements
cmux browser click <selector> [--snapshot-after]
cmux browser dblclick <selector> [--snapshot-after]
cmux browser hover <selector> [--snapshot-after]

# Focus and check
cmux browser focus <selector> [--snapshot-after]
cmux browser check <selector> [--snapshot-after]
cmux browser uncheck <selector> [--snapshot-after]

# Scroll
cmux browser scroll --selector <css> --dx <n> --dy <n>
cmux browser scroll-into-view <selector> [--snapshot-after]

# Type and fill
cmux browser type <selector> <text> [--snapshot-after]
cmux browser fill <selector> [text] [--snapshot-after]
cmux browser select <selector> <value> [--snapshot-after]

# Keyboard
cmux browser press <key> [--snapshot-after]
cmux browser keydown <key> [--snapshot-after]
cmux browser keyup <key> [--snapshot-after]

# Get element info
cmux browser get url
cmux browser get title
cmux browser get text <selector>
cmux browser get html <selector>
cmux browser get value <selector>
cmux browser get attr <selector> <name>
cmux browser get count <selector>
cmux browser get box <selector>
cmux browser get styles <selector>

# Element state
cmux browser is visible <selector>
cmux browser is enabled <selector>
cmux browser is checked <selector>

# Find elements
cmux browser find role <role>
cmux browser find text <text>
cmux browser find label <label>
cmux browser find placeholder <placeholder>
cmux browser find alt <alt>
cmux browser find title <title>
cmux browser find testid <testid>
cmux browser find first <selector>
cmux browser find last <selector>
cmux browser find nth <selector> <index>

# Frames
cmux browser frame <selector|main>

# Dialogs
cmux browser dialog accept [text]
cmux browser dialog dismiss [text]

# Downloads
cmux browser download wait
cmux browser download [--path <path>] [--timeout-ms <ms>]

# Cookies
cmux browser cookies get <name>
cmux browser cookies set <name> <value>
cmux browser cookies clear

# Local/Session storage
cmux browser storage local get <key>
cmux browser storage local set <key> <value>
cmux browser storage local clear
cmux browser storage session get <key>
cmux browser storage session set <key> <value>
cmux browser storage session clear

# Tabs
cmux browser tab new
cmux browser tab list
cmux browser tab switch <index>
cmux browser tab close <index>

# Console
cmux browser console list
cmux browser console clear

# Errors
cmux browser errors list
cmux browser errors clear

# Highlight element
cmux browser highlight <selector>

# State management
cmux browser state save <path>
cmux browser state load <path>

# Scripts
cmux browser addinitscript <script>
cmux browser addscript <script>
cmux browser addstyle <css>

# Evaluate JS
cmux browser eval <script>

# Identify surface
cmux browser identify [--surface <id|ref|index>]
```

---

### 11. Markdown Viewer

```bash
# Open markdown in formatted viewer
cmux markdown open <path>
```

---

### 12. App Focus Control

```bash
# Set app focus state
cmux set-app-focus active
cmux set-app-focus inactive
cmux set-app-focus clear

# Simulate app becoming active
cmux simulate-app-active
```

---

### 13. Tmux Compatibility Commands

```bash
# Capture pane content
cmux capture-pane [--workspace <id|ref>] [--surface <id|ref>] [--scrollback] [--lines <n>]

# Resize pane
cmux resize-pane --pane <id|ref> (-L|-R|-U|-D) [--amount <n>]

# Pipe pane output to command
cmux pipe-pane --command <shell-command> [--workspace <id|ref>] [--surface <id|ref>]

# Wait for signal
cmux wait-for -S <name>
cmux wait-for --signal <name> [--timeout <seconds>]

# Swap panes
cmux swap-pane --pane <id|ref> --target-pane <id|ref> [--workspace <id|ref>]

# Break/join panes
cmux break-pane [--workspace <id|ref>] [--pane <id|ref>] [--surface <id|ref>] [--no-focus]
cmux join-pane --target-pane <id|ref> [--workspace <id|ref>] [--pane <id|ref>] [--surface <id|ref>] [--no-focus]

# Window navigation
cmux next-window
cmux previous-window
cmux last-window

# Find window
cmux find-window [--content] [--select] <query>

# Clear history
cmux clear-history [--workspace <id|ref>] [--surface <id|ref>]

# Hooks
cmux set-hook --list
cmux set-hook --unset <event>
cmux set-hook <event> <command>

# Buffers
cmux set-buffer [--name <name>] <text>
cmux list-buffers
cmux paste-buffer [--name <name>] [--workspace <id|ref>] [--surface <id|ref>]

# Respawn pane
cmux respawn-pane [--workspace <id|ref>] [--surface <id|ref>] --command <cmd>

# Display message
cmux display-message -p <text>

# Copy mode
cmux copy-mode
cmux bind-key <key> <command>
cmux unbind-key <key>
cmux popup
```

---

### 14. Claude Teams Integration

```bash
# Run Claude with arguments in cmux
cmux claude-teams [claude-args...]
```

---

### 15. Themes

```bash
# Theme management
cmux themes list
cmux themes set <theme-name>
cmux themes clear
```

---

### 16. Feedback

```bash
# Send feedback
cmux feedback --email <email> --body <text>
cmux feedback --body <text> --image <path> --image <path>
```

---

### 17. Environment Variables

Key environment variables that cmux uses:

| Variable | Description |
|----------|-------------|
| `CMUX_WORKSPACE_ID` | Auto-set in cmux terminals, used as default workspace |
| `CMUX_TAB_ID` | Optional alias for tab-action/rename-tab |
| `CMUX_SURFACE_ID` | Auto-set in cmux terminals, used as default surface |
| `CMUX_SOCKET_PATH` | Override Unix socket path (default: ~/Library/Application Support/cmux/cmux.sock) |
| `CMUX_SOCKET_PASSWORD` | Socket authentication password |

---

## Spawn Named Pane

### Quick Spawn with Name

Since cmux doesn't have `--name` flag in `new-pane`, use this 2-step pattern:

```bash
# Get max surface number before
MAX_BEFORE=$(cmux tree --workspace workspace:1 | grep -o 'surface:[0-9]*' | grep -o '[0-9]*' | sort -n | tail -1)

# Create new split
cmux new-split right --workspace workspace:1

# Find new surface (higher number than before)
NEW_SURFACE="surface:$((MAX_BEFORE + 1))"

# Rename the new surface
cmux tab-action --action rename --surface "$NEW_SURFACE" --title "your-name"
```

---

## Common Patterns

### Open New Terminal in Directory
```bash
cmux new-split right --workspace <ws-id>
cmux send --surface <surface-id> "cd /path/to/directory && clear"
```

### Run Command in New Pane
```bash
cmux new-pane --type terminal --command "htop"
```

### Send Multiple Commands
```bash
cmux send --surface <surface-id> "git status"
cmux send-key --surface <surface-id> "Enter"
cmux send --surface <surface-id> "git log --oneline -5"
cmux send-key --surface <surface-id> "Enter"
```

### Open Project in cmux
```bash
cmux /path/to/project
```

### Focus Previous Window
```bash
cmux last-window
```

### Navigate Browser to URL
```bash
cmux browser goto https://google.com
cmux browser type input[name="q"] "search query"
cmux browser press Enter
```

---

## Error Handling

If a command fails, check:
1. Is cmux running? (use `cmux ping`)
2. Is the reference valid? (use `cmux tree` to see structure)
3. Is the socket path correct? (check `CMUX_SOCKET_PATH`)

Common error responses from cmux indicate missing or invalid references.
