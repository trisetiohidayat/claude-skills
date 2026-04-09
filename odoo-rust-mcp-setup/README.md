# Odoo Rust MCP Setup Skill

Automatically register Odoo instances with rust-mcp for Claude Code.

## Quick Start

1. Navigate to your Odoo project
2. Tell Claude: "Setup Odoo MCP instance"
3. Review detected configuration
4. Confirm to add instance

## What It Does

- Auto-detects Odoo configuration (odoo.conf, launch.json)
- Generates instance name automatically
- Writes to ~/.config/odoo-rust-mcp/instances.json
- Works with Odoo 14-19+

## Files

- `skill.md` - Skill definition (what Claude reads)
- `helpers.sh` - Shell functions for setup logic
- `README.md` - This file

## Requirements

- Bash shell
- jq (JSON parser)
- Odoo project with odoo.conf or odoo-*.conf

## Config Format

Writes to ~/.config/odoo-rust-mcp/instances.json:
```json
{
  "instance-name": {
    "db": "database",
    "password": "password",
    "url": "http://localhost:port",
    "username": "user",
    "version": "19.0"
  }
}
```

## Development

Test helpers directly:
```bash
source ~/.claude/skills/odoo-rust-mcp-setup/helpers.sh
setup_odoo_mcp_instance
```
