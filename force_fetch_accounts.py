#!/usr/bin/env python
"""
Force fetch new accounts from Airtable and restart all devices with reroll tasks
Use this when all devices are linked but the automatic detection isn't working
"""

import asyncio
import os
import json
from device_state_manager import device_state_manager
from airtable_stock_fetcher import check_and_fetch_all_accounts

async def force_fetch_and_restart():
    """Force fetch new accounts and restart all devices"""
    
    print("=" * 60)
    print("FORCE FETCH ACCOUNTS FROM AIRTABLE")
    print("=" * 60)
    
    # Check current status
    print("\n1. Checking current device status...")
    all_linked = True
    for i in range(1, 11):
        device_id = f"DEVICE{i}"
        state = device_state_manager.get_state(device_id)
        is_linked = state.get("isLinked", 0)
        account_id = state.get("AccountID", "")
        print(f"   {device_id}: isLinked={is_linked}, AccountID={account_id[:20] if account_id else 'None'}")
        if not is_linked:
            all_linked = False
    
    if not all_linked:
        print("\n⚠️ Warning: Not all devices are linked!")
        response = input("Do you want to continue anyway? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
    
    print("\n2. Closing all games...")
    try:
        from actions import run_adb_command
        BLEACH_PACKAGE_NAME = "com.klab.bleach"
        
        for i in range(1, 11):
            device_id = f"DEVICE{i}"
            print(f"   Closing game on {device_id}...")
            try:
                await run_adb_command(f"shell am force-stop {BLEACH_PACKAGE_NAME}", device_id)
            except Exception as e:
                print(f"   Failed to close on {device_id}: {e}")
        
        await asyncio.sleep(2)
    except ImportError:
        print("   Warning: Could not import actions module for closing games")
    
    print("\n3. Fetching new accounts from Airtable...")
    result = await check_and_fetch_all_accounts()
    
    if result:
        print("\n✅ SUCCESS! New accounts fetched.")
        
        # Verify the new states
        print("\n4. Verifying new device states...")
        for i in range(1, 11):
            device_id = f"DEVICE{i}"
            state = device_state_manager.get_state(device_id)
            email = state.get("Email", "")
            username = state.get("UserName", "")
            reroll_status = state.get("Reroll_Earse_GameData", 1)
            print(f"   {device_id}: Email={email[:20] if email else 'None'}, UserName={username}, Reroll={reroll_status}")
        
        # Check new stock number
        stock_file = os.path.join("device_states", "currentlyStock.json")
        if os.path.exists(stock_file):
            with open(stock_file, 'r') as f:
                stock_data = json.load(f)
                print(f"\n   New STOCK number: {stock_data['STOCK']}")
        
        print("\n5. Next steps:")
        print("   - All games have been closed")
        print("   - New accounts have been loaded")
        print("   - Reroll flags have been reset to 0")
        print("   - Run main.py to start the reroll cycle")
        print("\n   Command: python main.py")
    else:
        print("\n❌ Failed to fetch accounts.")
        print("Possible reasons:")
        print("1. Airtable API key not set")
        print("2. No matching records in Airtable")
        print("3. Network connection issues")

if __name__ == "__main__":
    asyncio.run(force_fetch_and_restart())
