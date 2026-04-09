#!/bin/bash

# Odoo Rust MCP Setup Helper Functions
# Used by odoo-rust-mcp-setup skill

set -euo pipefail

# Config paths
RUST_MCP_CONFIG_DIR="$HOME/.config/odoo-rust-mcp"
RUST_MCP_INSTANCES_FILE="$RUST_MCP_CONFIG_DIR/instances.json"

# Find workspace root (git repo or cwd)
find_workspace_root() {
    local cwd="$1"
    local root="$cwd"

    # Try to find .git directory
    while [ "$root" != "/" ] && [ ! -d "$root/.git" ]; do
        root=$(dirname "$root")
    done

    # If .git found, use it as root
    if [ -d "$root/.git" ]; then
        echo "$root"
    else
        echo "$cwd"
    fi
}

# Find odoo config file
find_odoo_config() {
    local workspace_root="$1"
    local launch_json="$2"
    local config_file=""

    # Priority 1: Check --config= arg in launch.json
    if [ -f "$launch_json" ]; then
        # Use sed for macOS compatibility (grep -P doesn't work on macOS)
        config_file=$(sed -n 's/.*--config=\([^"]*\).*/\1/p' "$launch_json" 2>/dev/null | head -1)
        if [ -n "$config_file" ]; then
            # Make absolute path if relative
            if [[ ! "$config_file" = /* ]]; then
                config_file="$workspace_root/$config_file"
            fi
            if [ -f "$config_file" ]; then
                echo "$config_file"
                return 0
            fi
        fi
    fi

    # Priority 2: Find odoo-*.conf files
    local conf_files=()
    while IFS= read -r -d '' file; do
        conf_files+=("$file")
    done < <(find "$workspace_root" -maxdepth 2 -name "odoo-*.conf" -print0 2>/dev/null)

    if [ ${#conf_files[@]} -eq 1 ]; then
        echo "${conf_files[0]}"
        return 0
    elif [ ${#conf_files[@]} -gt 1 ]; then
        # Multiple files - return list for selection
        printf '%s\n' "${conf_files[@]}"
        return 1
    fi

    # Priority 3: Fallback to odoo.conf
    if [ -f "$workspace_root/odoo.conf" ]; then
        echo "$workspace_root/odoo.conf"
        return 0
    fi

    # Priority 4: Check subdirectories
    for subdir in "config" "etc"; do
        if [ -f "$workspace_root/$subdir/odoo.conf" ]; then
            echo "$workspace_root/$subdir/odoo.conf"
            return 0
        fi
        # Also check for odoo-*.conf in subdirs
        local conf_files=()
        while IFS= read -r -d '' file; do
            conf_files+=("$file")
        done < <(find "$workspace_root/$subdir" -maxdepth 1 -name "odoo-*.conf" -print0 2>/dev/null)
        if [ ${#conf_files[@]} -eq 1 ]; then
            echo "${conf_files[0]}"
            return 0
        fi
    done

    return 1
}

# Find launch.json
find_launch_json() {
    local workspace_root="$1"

    if [ -f "$workspace_root/.vscode/launch.json" ]; then
        echo "$workspace_root/.vscode/launch.json"
        return 0
    fi

    return 1
}

# Extract values from odoo.conf
extract_odoo_conf() {
    local conf_file="$1"

    # Use sed for macOS compatibility (grep -P doesn't work on macOS)
    local db_host=$(sed -n 's/^[[:space:]]*db_host[[:space:]]*=[[:space:]]*\([^#]*\).*/\1/p' "$conf_file" 2>/dev/null | tr -d ' ' | head -1 || echo "localhost")
    local db_port=$(sed -n 's/^[[:space:]]*db_port[[:space:]]*=[[:space:]]*\([^#]*\).*/\1/p' "$conf_file" 2>/dev/null | tr -d ' ' | head -1 || echo "5432")
    local db_user=$(sed -n 's/^[[:space:]]*db_user[[:space:]]*=[[:space:]]*\([^#]*\).*/\1/p' "$conf_file" 2>/dev/null | tr -d ' ' | head -1 || echo "odoo")
    local db_password=$(sed -n 's/^[[:space:]]*db_password[[:space:]]*=[[:space:]]*\([^#]*\).*/\1/p' "$conf_file" 2>/dev/null | tr -d ' ' | head -1 || echo "odoo")
    local db_name=$(sed -n 's/^[[:space:]]*db_name[[:space:]]*=[[:space:]]*\([^#]*\).*/\1/p' "$conf_file" 2>/dev/null | tr -d ' ' | head -1 || echo "")

    # Build URL
    local protocol="http"
    local url="$protocol://$db_host:$db_port"

    # Output as JSON
    jq -n \
        --arg url "$url" \
        --arg db "$db_name" \
        --arg username "$db_user" \
        --arg password "$db_password" \
        --arg version "19.0" \
        '{url: $url, db: $db, username: $username, password: $password, version: $version}'
}

# Extract values from launch.json
extract_launch_json() {
    local launch_file="$1"
    local base_config="$2"  # JSON from odoo.conf

    # Use sed for macOS compatibility (grep -P doesn't work on macOS)
    local http_port=$(sed -n 's/.*--http-port=\([0-9]*\).*/\1/p' "$launch_file" 2>/dev/null | head -1)
    local database=$(sed -n 's/.*--database=\([^"]*\).*/\1/p' "$launch_file" 2>/dev/null | head -1)

    # Override base_config with launch.json values
    echo "$base_config" | jq \
        --arg port "$http_port" \
        --arg db "$database" \
        '
        if $port != "" then
            .url = ("http://localhost:" + $port)
        else
            .
        end |
        if $db != "" then
            .db = $db
        else
            .
        end
        '
}

# Generate instance name
generate_instance_name() {
    local db_name="$1"
    local conf_file="$2"
    local workspace_root="$3"

    # Priority 1: Use database name
    if [ -n "$db_name" ]; then
        echo "$db_name"
        return 0
    fi

    # Priority 2: Extract from config filename
    if [ -n "$conf_file" ]; then
        local basename=$(basename "$conf_file" .conf)
        if [[ "$basename" =~ ^odoo-(.+)$ ]]; then
            echo "${BASH_REMATCH[1]}"
            return 0
        fi
    fi

    # Priority 3: Use directory name
    local dirname=$(basename "$workspace_root")
    echo "${dirname}-odoo"
    return 0
}

# Write instance to rust-mcp config
write_instance_config() {
    local instance_name="$1"
    local instance_config="$2"  # JSON string

    # Ensure config directory exists
    mkdir -p "$RUST_MCP_CONFIG_DIR"

    # Read existing config or create new
    local existing_config="{}"
    if [ -f "$RUST_MCP_INSTANCES_FILE" ]; then
        existing_config=$(cat "$RUST_MCP_INSTANCES_FILE")
    fi

    # Check if instance already exists
    local exists=$(echo "$existing_config" | jq -r ".[\"$instance_name\"] != null")

    if [ "$exists" = "true" ]; then
        echo "Warning: Instance '$instance_name' already exists"
        return 1
    fi

    # Add instance to config
    local new_config=$(echo "$existing_config" | jq --argjson new "$instance_config" '.["'"$instance_name"'"] = $new')

    # Create backup
    if [ -f "$RUST_MCP_INSTANCES_FILE" ]; then
        cp "$RUST_MCP_INSTANCES_FILE" "$RUST_MCP_INSTANCES_FILE.bak"
    fi

    # Write new config
    echo "$new_config" | jq '.' > "$RUST_MCP_INSTANCES_FILE"

    echo "Instance '$instance_name' added successfully"
    return 0
}

# Update existing instance
update_instance_config() {
    local instance_name="$1"
    local instance_config="$2"  # JSON string

    if [ ! -f "$RUST_MCP_INSTANCES_FILE" ]; then
        echo "Error: Config file not found"
        return 1
    fi

    # Create backup
    cp "$RUST_MCP_INSTANCES_FILE" "$RUST_MCP_INSTANCES_FILE.bak"

    # Update instance
    local new_config=$(jq --argjson new "$instance_config" '.["'"$instance_name"'"] = $new' "$RUST_MCP_INSTANCES_FILE")

    echo "$new_config" | jq '.' > "$RUST_MCP_INSTANCES_FILE"

    echo "Instance '$instance_name' updated successfully"
    return 0
}

# Main setup function
setup_odoo_mcp_instance() {
    local workspace_root=$(find_workspace_root "$(pwd)")

    echo "=== Odoo Rust MCP Setup ==="
    echo "Workspace: $workspace_root"
    echo

    # Find config files
    echo "📂 Finding Odoo config files..."
    local launch_json=$(find_launch_json "$workspace_root")
    local odoo_conf=$(find_odoo_config "$workspace_root" "$launch_json")

    if [ $? -eq 1 ]; then
        echo "Multiple config files found:"
        echo "$odoo_conf"
        echo
        echo "Please specify which config to use manually"
        return 1
    fi

    if [ -z "$odoo_conf" ]; then
        echo "❌ Error: No Odoo config file found"
        echo "Looked for: odoo.conf, odoo-*.conf in workspace root and subdirectories"
        return 1
    fi

    echo "✓ Config found: $odoo_conf"
    [ -n "$launch_json" ] && echo "✓ Launch config: $launch_json"
    echo

    # Extract config
    echo "🔧 Extracting configuration..."
    local config=$(extract_odoo_conf "$odoo_conf")

    if [ -n "$launch_json" ]; then
        config=$(extract_launch_json "$launch_json" "$config")
    fi

    # Extract values for display
    local url=$(echo "$config" | jq -r '.url')
    local db=$(echo "$config" | jq -r '.db')
    local username=$(echo "$config" | jq -r '.username')
    local version=$(echo "$config" | jq -r '.version')

    echo "✓ URL: $url"
    echo "✓ Database: $db"
    echo "✓ Username: $username"
    echo "✓ Version: $version"
    echo

    # Generate instance name
    local instance_name=$(generate_instance_name "$db" "$odoo_conf" "$workspace_root")
    echo "📛 Instance name: $instance_name"
    echo

    # Show summary and ask confirmation
    echo "=== Configuration Summary ==="
    echo "Instance: $instance_name"
    echo "URL: $url"
    echo "Database: $db"
    echo "Username: $username"
    echo "Version: $version"
    echo
    echo "Add this instance to rust-mcp config?"

    # Return config for further processing
    echo "$config" | jq --arg name "$instance_name" '. + {instance_name: $name}'
    return 0
}
