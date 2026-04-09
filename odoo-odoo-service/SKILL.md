---
name: odoo-odoo-service
description: |
  Odoo service management - start, stop, restart Odoo server. Gunakan skill ini ketika:
  - Start Odoo server untuk development/testing
  - Stop Odoo server yang sedang running
  - Restart Odoo setelah upgrade module
  - Check status Odoo service
  - Multiple Odoo instances management

  Fokus pada process management dan port configuration.
---

# Odoo Service Management Skill

## Overview

Skill ini membantu management Odoo service/daemon - start, stop, restart.

## Starting Odoo

### Development Mode

```bash
# Basic start
./odoo-bin -c odoo19.conf

# Start dengan specific database
./odoo-bin -c odoo19.conf -d roedl

# Start dengan dev mode (reload on file change)
./odoo-bin -c odoo19.conf -d roedl --dev=all

# Start dengan specific port
./odoo-bin -c odoo19.conf -d roedl --http-port=8133
```

### Background Start

```bash
# Start di background dengan nohup
nohup ./odoo-bin -c odoo19.conf -d roedl > odoo.log 2>&1 &

# Start dengan screen
screen -S odoo
./odoo-bin -c odoo19.conf -d roedl
# Ctrl+A, D to detach

# Start dengan systemd (production)
sudo systemctl start odoo19
```

### Multiple Instances

```bash
# Instance 1 - Production (port 8069)
./odoo-bin -c odoo.conf -d roedl --http-port=8069

# Instance 2 - Development (port 8133)
./odoo-bin -c odoo19.conf -d roedl --http-port=8133

# Instance 3 - Testing (port 8134)
./odoo-bin -c odoo19.conf -d roedl_test --http-port=8134
```

## Stopping Odoo

### Graceful Stop

```bash
# Kill by PID
kill <PID>

# Kill with SIGTERM (graceful)
pkill -f "odoo-bin"
pkill -f "odoo-bin.*odoo19.conf"

# Using PID file
kill $(cat /var/run/odoo19.pid)
```

### Force Stop

```bash
# Kill with SIGKILL (force - may lose data)
pkill -9 -f "odoo-bin"

# Kill specific process
kill -9 <PID>

# Kill all Odoo processes
pkill -9 -f odoo
```

### Via Systemd

```bash
# Stop Odoo service
sudo systemctl stop odoo19

# Stop and disable
sudo systemctl disable odoo19
```

## Restarting Odoo

### Development Restart

```bash
# Stop and start again
pkill -f "odoo-bin.*odoo19.conf"
sleep 2
./odoo-bin -c odoo19.conf -d roedl &

# Or use systemd
sudo systemctl restart odoo19
```

### After Module Upgrade

```bash
# Option 1: Restart Odoo
pkill -f "odoo-bin.*odoo19.conf"
sleep 2
./odoo-bin -c odoo19.conf -d roedl > odoo.log 2>&1 &

# Option 2: Just restart, keep same process
# Not recommended - some changes require full restart
```

## Checking Status

### Process Status

```bash
# Check if Odoo is running
ps aux | grep odoo-bin

# Check specific port
lsof -i :8133
netstat -tlnp | grep 8133

# Check with pgrep
pgrep -f "odoo-bin.*odoo19.conf"
```

### Service Status

```bash
# Systemd status
sudo systemctl status odoo19

# Check log
tail -f /var/log/odoo19.log
tail -f odoo.log
```

### Database Connection

```bash
# Test connection
psql -h localhost -p 5432 -U odoo -d roedl -c "SELECT 1;"

# Check active connections
psql -h localhost -p 5432 -U odoo -d roedl -c "SELECT count(*) FROM pg_stat_activity WHERE datname = 'roedl';"
```

## Process Management

### Using PID File

```bash
# Start with PID file
./odoo-bin -c odoo19.conf -d roedl --pidfile=/var/run/odoo19.pid

# Check PID
cat /var/run/odoo19.pid

# Stop using PID
kill $(cat /var/run/odoo19.pid)
```

### Using systemd

```bash
# Create service file
sudo nano /etc/systemd/system/odoo19.service

# Content:
# [Unit]
# Description=Odoo 19
# After=postgresql.service
#
# [Service]
# Type=simple
# User=odoo
# ExecStart=/path/to/odoo-bin -c /path/to/odoo19.conf
# Restart=always
# RestartSec=10
#
# [Install]
# WantedBy=multi-user.target

# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable odoo19

# Start service
sudo systemctl start odoo19
```

### Using Supervisor

```bash
# Install supervisor
sudo apt install supervisor

# Create config
sudo nano /etc/supervisor/conf.d/odoo19.conf

# Content:
# [program:odoo19]
# command=/path/to/odoo-bin -c /path/to/odoo19.conf
# user=odoo
# autostart=true
# autorestart=true
# redirect_stderr=true
# stdout_logfile=/var/log/odoo19.log

# Reload and start
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start odoo19
```

## Port Management

### Default Ports

| Service | Default Port |
|---------|-------------|
| HTTP | 8069 |
| Longpolling | 8072 |

### Custom Ports

```bash
# Start dengan custom HTTP port
./odoo-bin -c odoo19.conf -d roedl --http-port=8133

# Start dengan custom longpolling port
./odoo-bin -c odoo19.conf -d roedl --longpolling-port=8134

# Disable longpolling (for testing)
./odoo-bin -c odoo19.conf -d roedl --longpolling-port=0
```

### Port Conflict Resolution

```bash
# Find what's using a port
lsof -i :8133

# Kill process using port
kill $(lsof -t -i:8133)

# Or
fuser -k 8133/tcp
```

## Configuration Tips

### Development Config

```ini
[options]
; Basic
admin_passwd = admin
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
addons_path = /path/to/odoo19/addons,/path/to/enterprise

; Development
dev = all
log-handler = :DEBUG
log-level = debug

; Ports
http_port = 8133
longpolling_port = 8133

; Performance
workers = 0
max_cron_threads = 1
```

### Multi-Instance Config

```ini
[options]
; Different database per instance
db_host = localhost
db_port = 5432

; Different port
http_port = 8134

; Different addons path
addons_path = /path/to/custom_addons_19,/path/to/odoo19/addons
```

## Common Issues

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8133

# Kill and restart
kill -9 <PID>
./odoo-bin -c odoo19.conf -d roedl
```

### Database Connection Error

```bash
# Check PostgreSQL
pg_isready -h localhost -p 5432

# Check credentials
psql -h localhost -p 5432 -U odoo -l

# Restart PostgreSQL if needed
sudo systemctl restart postgresql
```

### Permission Denied

```bash
# Check file permissions
ls -la odoo-bin
ls -la odoo19.conf

# Fix permissions
chmod +x odoo-bin
chown odoo:odoo odoo19.conf
```

### Module Not Found

```bash
# Check addons path
./odoo-bin -c odoo19.conf --stop-after-init --test-tags='' 2>&1 | grep "addons path"

# Verify path in config
grep "addons_path" odoo19.conf
```

## Quick Reference

```bash
# Start Odoo
./odoo-bin -c odoo19.conf -d roedl

# Start in background
nohup ./odoo-bin -c odoo19.conf -d roedl > odoo.log 2>&1 &

# Check running
ps aux | grep odoo-bin

# Check port
lsof -i :8133

# Stop Odoo
pkill -f "odoo-bin.*odoo19.conf"

# Restart
pkill -f "odoo-bin.*odoo19.conf"
sleep 2
./odoo-bin -c odoo19.conf -d roedl &
```

## Related Skills

- `odoo-environment`: Check environment configuration
- `odoo-db-management`: Database operations
- `odoo-module-install`: Module installation
