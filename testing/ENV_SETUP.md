# Environment Variables Setup

## Overview
All sensitive credentials (Airtable API keys, S3 credentials) are now stored in a `.env` file instead of being hardcoded.

## Setup Instructions

### 1. Local Setup
The `.env` file already exists on your local machine. No action needed.

### 2. Server-Specific .env Files (Automatic Sync)
**NEW FEATURE**: You can now have different credentials for each server!

Create server-specific files locally:
- `.env1` - Configuration for RDP#1
- `.env2` - Configuration for RDP#2  
- `.env3` - Configuration for RDP#3

**How it works:**
1. Create `.env1`, `.env2`, `.env3` in your local project directory
2. Each file should contain the environment variables for that specific server
3. When you run `python project_sync.py`, the script will:
   - Sync `.env1` to RDP#1 as `.env`
   - Sync `.env2` to RDP#2 as `.env`
   - Sync `.env3` to RDP#3 as `.env`

**Example workflow:**
```bash
# Copy your local .env as templates
cp .env .env1
cp .env .env2
cp .env .env3

# Edit each file with server-specific credentials
nano .env1  # Edit for RDP#1
nano .env2  # Edit for RDP#2
nano .env3  # Edit for RDP#3

# Run sync - each server gets its own .env automatically!
python project_sync.py
```

### 3. Manual Setup (Alternative)
If you don't use server-specific files, you can still manually copy:

**Via SSH:**
```bash
# For RDP#1
scp .env fadi@37.27.127.250:/c/Users/Administrator/Desktop/Bleach_10x/

# For RDP#2
scp .env anas@37.27.226.185:/c/Users/Administrator/Desktop/Bleach_10x/

# For RDP#3
scp .env karek@37.27.226.186:/c/Users/karek/Desktop/Bleach_10x/
```

### 4. Verify Setup
On each remote machine, check that:
1. `.env` file exists in the project directory
2. File contains all required variables (see `.env.example`)

## Security Notes
- ✅ `.env` is excluded from git (in `.gitignore`)
- ✅ `.env` is excluded from project sync (in `project_sync.py`)
- ✅ Never commit `.env` to version control
- ✅ Use `.env.example` as a template (no real credentials)

## Required Environment Variables

### Airtable Main
- `AIRTABLE_API_KEY` - Airtable API key
- `AIRTABLE_BASE_ID` - Main base ID
- `AIRTABLE_TABLE_ID` - Main table ID

### Airtable 2FA
- `AIRTABLE_2FA_BASE_ID` - 2FA base ID
- `AIRTABLE_2FA_TABLE_ID` - 2FA table ID

### S3 Storage
- `S3_ACCESS_KEY_ID` - S3 access key
- `S3_SECRET_ACCESS_KEY` - S3 secret key
- `S3_ENDPOINT` - S3 endpoint URL
- `S3_BUCKET_NAME` - S3 bucket name
- `S3_REGION` - S3 region

## Files Updated
The following files now load credentials from `.env`:
- `airtable_helper.py` - 2FA code retrieval
- `airtable_import.py` - Import from Airtable
- `airtable_stock_fetcher.py` - Stock fetching
- `airtable_sync.py` - Sync to Airtable + S3

## Troubleshooting
If you get errors about missing environment variables:
1. Verify `.env` file exists in the project root
2. Check file contains all required variables
3. Ensure no typos in variable names
4. Restart the application after creating/updating `.env`
