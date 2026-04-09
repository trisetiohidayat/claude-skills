---
name: odoo-rust-mcp-setup
description: Auto-setup Odoo MCP instances by detecting odoo.conf and launch.json configuration
---

# Odoo Rust MCP Setup

## Overview

Automatically register Odoo instances with rust-mcp by detecting configuration from project files. This skill eliminates manual JSON editing and works from any Odoo project directory.

### What It Does

1. Finds Odoo config files (odoo.conf, odoo-*.conf, launch.json)
2. Extracts connection details (URL, database, credentials)
3. Generates instance name automatically
4. Writes to ~/.config/odoo-rust-mcp/instances.json

### Trigger Modes

- **Manual:** Invoke explicitly with "setup MCP", "register Odoo instance"
- **Hybrid:** Auto-detects when MCP tool returns "Unknown Odoo instance" error

## When to Use

**Use this skill when:**
- Starting work on a new Odoo project
- MCP tool returns "Unknown Odoo instance" error
- User explicitly asks to setup/register MCP instance
- Need to add multiple Odoo environments to rust-mcp

**Don't use for:**
- Modifying existing instance config (use manual edit)
- Removing instances (not implemented yet)
- Debugging MCP connection issues (check rust-mcp logs)

## Usage

### Basic Flow

1. **Navigate to your Odoo project directory**
   ```bash
   cd /path/to/odoo-project
   ```

2. **Invoke the skill**
   - Tell Claude: "Setup Odoo MCP instance" or "Register this Odoo instance"
   - Or when MCP tool returns error, Claude will auto-detect

3. **Review detected configuration**
   - Skill shows: URL, database, username, version
   - Verify the values are correct

4. **Confirm to add instance**
   - Skill writes to ~/.config/odoo-rust-mcp/instances.json
   - Instance is now available to MCP tools

### What Gets Detected

**From odoo.conf:**
- Database connection (host, port, user, password)
- Default database name (db_name)

**From launch.json:**
- HTTP port override (--http-port)
- Database override (--database)
- Config file path (--config)

**Priority:** launch.json args OVERRIDE odoo.conf values

### Instance Naming

Auto-generated in this priority:
1. Database name from config
2. Config filename (odoo-prod.conf → "prod")
3. Workspace directory name

## Error Handling

### Config File Not Found

**Symptom:** "No Odoo config file found"

**Solution:**
- Verify odoo.conf or odoo-*.conf exists in project root
- Check subdirectories: ./config/, ./etc/
- Specify config path explicitly if using custom location

### Multiple Config Files

**Symptom:** Multiple odoo-*.conf files detected

**Solution:**
- Skill will list all found config files
- Specify which one to use
- Or rename configs to be more specific

### Invalid Config Format

**Symptom:** "Failed to parse config file"

**Solution:**
- Check odoo.conf syntax (INI format)
- Check launch.json syntax (JSON format)
- Look for typos in key names

### Instance Already Exists

**Symptom:** "Instance 'xxx' already exists"

**Solution:**
- Use manual edit to update existing instance
- Or choose different instance name
- Use --force flag to overwrite (not implemented yet)

### Permission Denied

**Symptom:** "Cannot write to ~/.config/odoo-rust-mcp/instances.json"

**Solution:**
```bash
mkdir -p ~/.config/odoo-rust-mcp
chmod 755 ~/.config/odoo-rust-mcp
```

## Testing

### Test Setup

1. **Verify helpers.sh works:**
   ```bash
   source ~/.claude/skills/odoo-rust-mcp-setup/helpers.sh
   setup_odoo_mcp_instance
   ```

2. **Check output config:**
   ```bash
   cat ~/.config/odoo-rust-mcp/instances.json | jq .
   ```

3. **Test MCP connection:**
   ```bash
   # Use MCP tool with the new instance name
   ```

### Validation Checklist

After running the skill:
- [ ] Instance appears in instances.json
- [ ] JSON is valid (jq can parse it)
- [ ] MCP tools can access the instance
- [ ] Backup file created (.bak)
- [ ] Values are correct (URL, database, etc.)
