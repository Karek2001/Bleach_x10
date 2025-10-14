# Project Sync Tool

Automatic synchronization tool to mirror your local development environment to remote servers.

## Features

✅ **Mirror Mode (Default)** - Any change in local environment is reflected on remote servers:
  - ➕ New files are copied
  - ✏️ Modified files are updated
  - ❌ Deleted files are removed from remotes

✅ **Smart Exclusions** - Automatically excludes:
  - `.env*` files (server-specific configs synced separately)
  - `device_states/` folder
  - `stock_images/` folder
  - `testing/` folder
  - Git and cache files

✅ **Server-Specific Configs** - Each server can have different `.env` credentials

✅ **Parallel Sync** - All servers sync simultaneously for speed

## Usage

### Basic Sync (Mirror Mode - Default)
```bash
python project_sync.py
```
This will:
- Sync all changed files
- Delete files on remote that don't exist locally
- Respect exclusions (device_states, stock_images, etc.)

### Force Sync All Files
```bash
python project_sync.py --force
```
Forces re-sync of all files, even if unchanged.

### Disable Mirror Mode (No Deletions)
```bash
python project_sync.py --no-mirror
```
Only syncs new/modified files, doesn't delete anything.

### Auto-Watch Mode
```bash
python project_sync.py --watch 60
```
Automatically syncs every 60 seconds.

### Combine Options
```bash
python project_sync.py --force --watch 30
```

## Server Configuration

### Server-Specific .env Files

Each server gets its own environment variables:

**Local files:**
- `.env1` → Syncs to RDP#1 as `.env`
- `.env2` → Syncs to RDP#2 as `.env`
- `.env3` → Syncs to RDP#3 as `.env`

**Setup:**
```bash
# Quick setup
./setup_server_envs.sh

# Or manually
cp .env .env1
cp .env .env2
cp .env .env3

# Edit each with server-specific credentials
nano .env1
nano .env2
nano .env3
```

## What Gets Synced

**Included file types:**
- `.py` - Python source files
- `.json` - Configuration files
- `.png` - Template images (in templates/ folder)
- `.txt`, `.md` - Documentation
- `.sh` - Shell scripts

**Excluded:**
- `.env`, `.env1`, `.env2`, `.env3` (synced separately)
- `device_states/` - Local device data
- `stock_images/` - Large image assets
- `testing/` - Test files
- `__pycache__/`, `.git/` - System files

## Examples

### Workflow 1: Daily Development
```bash
# Make changes to code
nano main.py

# Delete a test file
rm old_test.py

# Sync changes (including deletion)
python project_sync.py
```
**Result:** `main.py` updated on all servers, `old_test.py` deleted from all servers.

### Workflow 2: Initial Setup
```bash
# First time sync - push everything
python project_sync.py --force

# Setup server-specific env files
./setup_server_envs.sh
nano .env1 .env2 .env3

# Sync env files
python project_sync.py
```

### Workflow 3: Continuous Development
```bash
# Start auto-sync in background
python project_sync.py --watch 60 &

# Work on your code normally
# Changes auto-sync every 60 seconds

# Stop auto-sync
kill %1
```

## Troubleshooting

### Deletions not working
- Check that mirror mode is enabled (default)
- Run `python project_sync.py --force` to reset

### .env not syncing
- Make sure `.env1`, `.env2`, `.env3` exist
- Check file isn't corrupted
- Verify server_number is set in config

### Files not syncing
- Check if file type is supported
- Verify file isn't in exclusion list
- Try `python project_sync.py --force`

## Security Notes

🔒 **Never commit credentials:**
- `.env`, `.env1`, `.env2`, `.env3` are in `.gitignore`
- Use `.env.example` as template for others

🔒 **SSH credentials in config:**
- Consider using SSH keys instead of passwords
- Keep `project_sync.py` secure

## Remote Server Paths

- **RDP#1**: `C:/Users/Administrator/Desktop/Bleach_10x`
- **RDP#2**: `C:/Users/Administrator/Desktop/Bleach_10x`
- **RDP#3**: `C:/Users/karek/Desktop/Bleach_10x`
