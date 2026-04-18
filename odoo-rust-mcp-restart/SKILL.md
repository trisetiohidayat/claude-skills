---
name: odoo-rust-mcp-restart
description: Restart the rust-mcp Odoo MCP server using brew services. Use when user asks to "restart MCP", "restart rust-mcp", "reload MCP service", "restart Odoo MCP", or when the MCP connection is not working and needs to be restarted.
---

# Odoo Rust MCP Restart

## Overview

Restarts the rust-mcp Homebrew service. This is the recommended way to restart rust-mcp when:
- MCP connection is not working
- Configuration changes need to take effect
- MCP returns errors or timeouts

**Prerequisite:** rust-mcp must be installed and registered as a Homebrew service.

## When to Use

**Use this skill when:**
- User asks to "restart MCP", "restart rust-mcp", "reload MCP"
- User says "MCP not working", "MCP error", "MCP timeout"
- Configuration file was updated and needs reload
- MCP tools return "connection refused" or similar errors

## Restart Procedure

### Step 1: Check Service Status

Verify rust-mcp is registered as a brew service:
```bash
brew services list | grep rust-mcp
```

### Step 2: Restart Service

Restart using Homebrew services:
```bash
brew services restart rust-mcp
```

### Step 3: Verify Restart

Check that service is now "started":
```bash
brew services list | grep rust-mcp
```

Also verify process is running:
```bash
ps aux | grep rust-mcp | grep -v grep
```

## Output Format

Report:
- Service status before restart
- Command executed
- Service status after restart
- Process status

## Error Handling

### Service Not Found

**Symptom:** "Service `rust-mcp` not found"

**Solution:**
- Install rust-mcp: `brew install rust-mcp`
- Or check if service name is different: `brew services list`

### Service Fails to Start

**Symptom:** Service shows "error" or process not running

**Solution:**
- Check service logs: `brew services log rust-mcp`
- Check configuration: `cat ~/.config/odoo-rust-mcp/instances.json | jq .`
- Try manual start: `brew services start rust-mcp`

### Permission Denied

**Symptom:** "Permission denied" when running brew services

**Solution:**
- Ensure running as correct user (service installed for current user)
- Check Homebrew permissions

## Success Criteria

After restart:
- [ ] Service shows "started" status
- [ ] rust-mcp process is running
- [ ] MCP tools can connect
