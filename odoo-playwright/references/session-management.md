# Browser Session Management

Run multiple isolated browser sessions concurrently with state persistence and auto-reconnect.

## Named Browser Sessions

Use `-s` flag to isolate browser contexts:

```bash
# Browser 1: Authentication flow
playwright-cli -s=auth open https://app.example.com/login

# Browser 2: Public browsing (separate cookies, storage)
playwright-cli -s=public open https://example.com

# Commands are isolated by browser session
playwright-cli -s=auth fill e1 "user@example.com"
playwright-cli -s=public snapshot
```

## Session Auto-Reconnect

```bash
# playwright-cli auto-detects expired sessions and re-authenticates
playwright-cli -s=odoo-test open http://localhost:8069/web

# If session is dead (expired/timeout), playwright-cli automatically:
# 1. Detects: eval checking odoo.session_info returns undefined/timeout
# 2. Navigates to /web/login
# 3. Re-fills credentials
# 4. Restores original URL

# Force re-authentication (ignore cached session)
playwright-cli -s=odoo-test open http://localhost:8069/web --force-reauth

# Check session health manually
playwright-cli -s=odoo-test eval "() => typeof odoo !== 'undefined' && odoo.session_info ? 'alive' : 'dead'"
# alive = session OK | dead = needs re-auth
```

## Session List

```bash
# List all active browser sessions with their state
playwright-cli list

# Output:
# SESSION    STATUS  URL                                          LAST ACTIVE
# default    alive   http://localhost:8069/web#action=sale...     30s ago
# odoo-test  alive   http://localhost:8069/web#model=sale.order   2m ago
# scrape-01  dead    (session expired)                           15m ago

# Attach to an active session
playwright-cli attach odoo-test

# Attach with auto-reconnect (if session dead, re-authenticate first)
playwright-cli attach odoo-test --auto-reconnect
```

## Browser Session Isolation Properties
- Cookies
- LocalStorage / SessionStorage
- IndexedDB
- Cache
- Browsing history
- Open tabs

## Browser Session Commands

```bash
# List all browser sessions
playwright-cli list

# Stop a browser session (close the browser)
playwright-cli close                # stop the default browser
playwright-cli -s=mysession close   # stop a named browser

# Stop all browser sessions
playwright-cli close-all

# Forcefully kill all daemon processes (for stale/zombie processes)
playwright-cli kill-all

# Delete browser session user data (profile directory)
playwright-cli delete-data                # delete default browser data
playwright-cli -s=mysession delete-data   # delete named browser data
```

## Environment Variable

Set a default browser session name via environment variable:

```bash
export PLAYWRIGHT_CLI_SESSION="mysession"
playwright-cli open example.com  # Uses "mysession" automatically
```

## Common Patterns

### Concurrent Scraping

```bash
#!/bin/bash
# Scrape multiple sites concurrently

# Start all browsers
playwright-cli -s=site1 open https://site1.com &
playwright-cli -s=site2 open https://site2.com &
playwright-cli -s=site3 open https://site3.com &
wait

# Take snapshots from each
playwright-cli -s=site1 snapshot
playwright-cli -s=site2 snapshot
playwright-cli -s=site3 snapshot

# Cleanup
playwright-cli close-all
```

### A/B Testing Sessions

```bash
# Test different user experiences
playwright-cli -s=variant-a open "https://app.com?variant=a"
playwright-cli -s=variant-b open "https://app.com?variant=b"

# Compare
playwright-cli -s=variant-a screenshot
playwright-cli -s=variant-b screenshot
```

### Persistent Profile

By default, browser profile is kept in memory only. Use `--persistent` flag on `open` to persist the browser profile to disk:

```bash
# Use persistent profile (auto-generated location)
playwright-cli open https://example.com --persistent

# Use persistent profile with custom directory
playwright-cli open https://example.com --profile=/path/to/profile
```

## Default Browser Session

When `-s` is omitted, commands use the default browser session:

```bash
# These use the same default browser session
playwright-cli open https://example.com
playwright-cli snapshot
playwright-cli close  # Stops default browser
```

## Browser Session Configuration

Configure a browser session with specific settings when opening:

```bash
# Open with config file
playwright-cli open https://example.com --config=.playwright/my-cli.json

# Open with specific browser
playwright-cli open https://example.com --browser=firefox

# Open in headed mode
playwright-cli open https://example.com --headed

# Open with persistent profile
playwright-cli open https://example.com --persistent
```

## Best Practices

### 1. Name Browser Sessions Semantically

```bash
# GOOD: Clear purpose
playwright-cli -s=github-auth open https://github.com
playwright-cli -s=docs-scrape open https://docs.example.com

# AVOID: Generic names
playwright-cli -s=s1 open https://github.com
```

### 2. Always Clean Up

```bash
# Stop browsers when done
playwright-cli -s=auth close
playwright-cli -s=scrape close

# Or stop all at once
playwright-cli close-all

# If browsers become unresponsive or zombie processes remain
playwright-cli kill-all
```

### 3. Delete Stale Browser Data

```bash
# Remove old browser data to free disk space
playwright-cli -s=oldsession delete-data
```
