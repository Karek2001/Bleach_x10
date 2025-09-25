#!/usr/bin/env python
"""
Fix wrongly named device files and force fetch new accounts
"""

import asyncio
import os
import json
import glob
from device_state_manager import device_state_manager
from airtable_stock_fetcher import check_and_fetch_all_accounts

async def fix_and_fetch():
    """Fix device files and force fetch"""
    
    print("=" * 60)
    print("FIX DEVICE FILES AND FETCH NEW ACCOUNTS")
    print("=" * 60)
    
    # Step 1: Clean up wrongly named files
    print("\n1. Cleaning up wrongly named files...")
    device_states_dir = "device_states"
    
    # Find all DEVICE_DEVICE*.json files
    wrong_files = glob.glob(os.path.join(device_states_dir, "DEVICE_DEVICE*.json"))
    if wrong_files:
        print(f"   Found {len(wrong_files)} wrongly named files:")
        for file in wrong_files:
            print(f"   - {os.path.basename(file)}")
            os.remove(file)
            print(f"     Deleted: {os.path.basename(file)}")
    else:
        print("   No wrongly named files found.")
    
    # Step 2: Check current device status
    print("\n2. Checking current device status...")
    all_linked = True
    for i in range(1, 11):
        device_id = f"DEVICE{i}"
        device_file = os.path.join(device_states_dir, f"{device_id}.json")
        
        if os.path.exists(device_file):
            with open(device_file, 'r') as f:
                state = json.load(f)
            is_linked = state.get("isLinked", 0)
            account_id = state.get("AccountID", "")
            print(f"   {device_id}: isLinked={is_linked}, AccountID={account_id[:20] if account_id else 'None'}")
            if not is_linked:
                all_linked = False
        else:
            print(f"   {device_id}: File not found")
            all_linked = False
    
    if all_linked:
        print("\n✅ All devices are linked!")
        print("\n3. Fetching new accounts from Airtable...")
        result = await check_and_fetch_all_accounts()
        
        if result:
            print("\n✅ SUCCESS! New accounts fetched.")
            
            # Verify the new states
            print("\n4. Verifying new device files...")
            for i in range(1, 11):
                device_id = f"DEVICE{i}"
                device_file = os.path.join(device_states_dir, f"{device_id}.json")
                
                if os.path.exists(device_file):
                    with open(device_file, 'r') as f:
                        state = json.load(f)
                    email = state.get("Email", "")
                    username = state.get("UserName", "")
                    reroll_status = state.get("Reroll_Earse_GameData", 1)
                    print(f"   {device_id}: Email={email[:20] if email else 'None'}, Reroll={reroll_status}")
                else:
                    print(f"   {device_id}: File not found after fetch!")
            
            # Check new stock number
            stock_file = os.path.join(device_states_dir, "currentlyStock.json")
            if os.path.exists(stock_file):
                with open(stock_file, 'r') as f:
                    stock_data = json.load(f)
                    print(f"\n   New STOCK number: {stock_data['STOCK']}")
            
            print("\n5. Next steps:")
            print("   - Run main.py to start the reroll cycle")
            print("   - The system will now properly detect linked devices")
        else:
            print("\n❌ Failed to fetch accounts.")
    else:
        print("\n⚠️ Not all devices are linked yet.")
        print("You may need to:")
        print("1. Complete the linking process for all devices")
        print("2. Or manually trigger the fetch with force_fetch_accounts.py")

if __name__ == "__main__":
    asyncio.run(fix_and_fetch())
