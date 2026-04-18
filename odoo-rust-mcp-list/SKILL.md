---
name: odoo-rust-mcp-list
description: List all registered Odoo rust-mcp instances and their connection details. Use when user asks to "list MCP instances", "show Odoo instances", "list Odoo connections", "check rust-mcp instances", or wants to see all configured Odoo MCP connections. This skill reads ~/.config/odoo-rust-mcp/instances.json and displays a formatted table of all instances.
---

# Odoo Rust MCP List

## Overview

Lists all registered Odoo rust-mcp instances from `~/.config/odoo-rust-mcp/instances.json`. Displays connection details including URL, database, username, and version in a formatted table.

## When to Use

**Use this skill when:**
- User asks to "list MCP instances"
- User asks to "show Odoo instances"
- User asks to "list Odoo connections"
- User asks to "check rust-mcp instances"
- User wants to see all configured Odoo MCP connections
- User wants to verify which instances are registered

## Usage

Simply invoke the skill and it will:
1. Read `~/.config/odoo-rust-mcp/instances.json`
2. Parse and display instances in a formatted table
3. Show connection details for each instance

## Output Format

Display instances in a clear table with columns:
- **Instance Name** - The key from instances.json
- **URL** - Odoo server URL
- **Database** - Database name
- **Username** - Login username
- **Version** - Odoo version

Also show:
- Total count of instances
- File location
- Last modified time (if available)

## Error Handling

### No instances found

**Symptom:** "No instances found" or empty config

**Solution:**
- Check if file exists at `~/.config/odoo-rust-mcp/instances.json`
- If not, no MCP instances have been configured yet
- User can use `odoo-rust-mcp-setup` skill to add instances

### Invalid JSON format

**Symptom:** JSON parsing error

**Solution:**
- File may be corrupted
- Show raw content for manual review
- Suggest checking file manually
