---
description: Initialize a new Odoo project with version selection and repository cloning
---

You are helping the user initialize a new Odoo project from scratch.

## Steps

1. **Ask for project name**:
   - Use AskUserQuestion to get the project name
   - This will be used for folder naming and configuration

2. **Ask for Odoo version** using AskUserQuestion:
   - Header: "Odoo Version"
   - Question: "Which Odoo version do you want to use?"
   - Options:
     - "17.0" - Latest stable (17.0)
     - "16.0" - Previous stable (16.0)
     - "15.0" - Older stable (15.0)
     - "14.0" - Older stable (14.0)
   - multiSelect: false

3. **Ask for custom repositories** (optional):
   - Use AskUserQuestion with multiSelect=true
   - Header: "Custom Repos"
   - Question: "Do you want to add custom addon repositories? (optional)"
   - Options:
     - "Skip" - No custom repos, continue with official Odoo only
     - "Enterprise" - Add Odoo Enterprise repository
     - "Custom" - Specify custom repository URLs

4. **If Enterprise or Custom is selected**, ask for repository URLs:
   - For Enterprise: ask for the enterprise repo URL (typically: https://github.com/odoo/enterprise.git)
   - For Custom: allow user to input multiple repo URLs separated by comma
   - Store these for later cloning

5. **Determine Odoo base directory**:
   - Check common locations: ~/odoo, ~/projects/odoo, or current project parent directory
   - Ask user to confirm or specify the base Odoo directory where official Odoo will be cloned
   - Create directory if it doesn't exist

6. **Clone official Odoo repository**:
   - Official URL: https://github.com/odoo/odoo.git
   - Clone to: `{base_odoo_dir}/odoo{version}-{project_name}/odoo`
   - Use the branch corresponding to the selected version (e.g., `17.0`, `16.0`)
   - Command: `git clone -b {version} --depth 1 https://github.com/odoo/odoo.git {target_path}`

7. **Clone additional repositories** (if specified):
   - For each custom/enterprise repo:
     - Clone to: `{base_odoo_dir}/enterprise-{version}-{date}/enterprise` (for enterprise)
     - Or custom path based on repo name
     - Use same version branch

8. **Create project structure**:

   a. **Create directories**:
   ```bash
   mkdir -p data
   mkdir -p .vscode
   mkdir -p addons/{project_name}-core,{project_name}-extra
   ```

   b. **Create odoo.conf**:
   - Template based on project/suqma/odoo-mac.conf
   - Replace paths with actual project paths
   - Set database configuration (db_user=odoo, db_password=odoo, db_host=localhost, db_port=5432)
   - Configure addons_path to include:
     * Enterprise addons (if cloned)
     * Official Odoo addons
     * Official Odoo odoo/addons
     * Project custom addons (project-{name}-core, project-{name}-extra)
   - Set data_dir to project data directory
   - Include common settings (limit_time_CPU, limit_time_real, log_level, etc.)

   c. **Create .vscode/launch.json**:
   - Template based on project/suqma/.vscode/launch.json
   - Set name to "Odoo {PROJECT_NAME} {VERSION}"
   - **IMPORTANT**: Point python to project directory's venv (e.g., `${workspaceFolder}/venv/bin/python`)
   - Set program path to cloned Odoo odoo-bin
   - Set config file path to created odoo.conf
   - Include common args: --dev=xml, --http-port (use unique port like 8069 + project hash)
   - Add database argument placeholder

   d. **Create .gitignore**:
   ```
   *.pyc
   __pycache__/
   *.pyo
   *.pyd
   .Python
   venv/
   *.egg-info/
   .eggs/
   dist/
   build/
   data/
   *.log
   .DS_Store
   *.conf
   !odoo.conf
   ```

   e. **Create requirements.txt** (if needed):
   - Basic Odoo requirements (optional, can reference official Odoo requirements)

   f. **Create README.md** with:
   - Project name and description
   - Odoo version
   - Setup instructions
   - Repository links

9. **Create Python virtual environment in project directory**:
   ```bash
   # Create venv IN the project directory (not in Odoo base!)
   python3 -m venv venv
   source venv/bin/activate

   # Install requirements from Odoo base's requirements.txt
   pip install -r {odoo_path}/requirements.txt
   ```

   **IMPORTANT**: The venv MUST be created inside the project directory (e.g., `/path/to/myproject/venv/`), NOT in the Odoo base folder. This ensures:
   - Each project has its own isolated Python environment
   - Dependencies don't conflict between projects
   - Easy to delete/recreate without affecting Odoo base

10. **Summary**:
    Show what was created:
    - Project directory structure
    - Cloned repositories with paths
    - Configuration files created
    - Next steps (install dependencies, configure database, run Odoo)

## Important Notes

- Always use `--depth 1` for cloning to save time and space
- If user already has Odoo cloned elsewhere, ask if they want to reuse it
- For Enterprise repos, warn that they need valid Odoo Enterprise credentials/license
- Handle errors gracefully (network issues, git not available, etc.)
- Use absolute paths in all configuration files
- For macOS, detect pg_path automatically (common locations: /opt/homebrew/opt/postgresql@*/bin, /usr/local/opt/postgresql@*/bin)

## Example Output

```
## Odoo Project Initialization Complete

Project: duniatex
Version: 17.0

### Created Structure:
/Users/tri-mac/project/duniatex/
├── .vscode/
│   └── launch.json
├── .claude/
│   └── skills/
│       └── odoo-init.md
├── data/
├── venv/                        # <-- venv di project directory ini
├── addons/
│   ├── duniatex-core/
│   └── duniatex-extra/
├── odoo.conf
├── .gitignore
└── README.md

### Cloned Repositories:
- Odoo 17.0: /Users/tri-mac/odoo/odoo17-duniatex/odoo
- Enterprise 17.0: /Users/tri-mac/odoo/enterprise-duniatex-17.0/enterprise

### Next Steps:
1. Activate virtual environment: source venv/bin/activate
2. (Dependencies sudah terinstall dari requirements.txt saat inisialisasi)
3. Create PostgreSQL database: createdb duniatex
4. Run Odoo: Use F5 in VS Code or: python /Users/tri-mac/odoo/odoo17-duniatex/odoo/odoo-bin -c odoo.conf
```
