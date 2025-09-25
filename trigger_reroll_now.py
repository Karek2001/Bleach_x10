#!/usr/bin/env python
"""
Immediately trigger the reroll cycle for all linked devices
This bypasses the automatic detection and forces the cycle to start
"""

import asyncio
import os
import json
import subprocess
from datetime import datetime

async def trigger_reroll_now():
    """Force trigger reroll cycle immediately"""
    
    print("=" * 60)
    print("FORCE TRIGGER REROLL CYCLE")
    print("=" * 60)
    
    # Step 1: Verify all devices are actually linked
    print("\n1. Verifying device link status...")
    device_states_dir = "device_states"
    all_linked = True
    linked_count = 0
    
    for i in range(1, 11):
        device_id = f"DEVICE{i}"
        device_file = os.path.join(device_states_dir, f"{device_id}.json")
        
        if os.path.exists(device_file):
            with open(device_file, 'r') as f:
                state = json.load(f)
            is_linked = state.get("isLinked", 0)
            if is_linked:
                linked_count += 1
                print(f"   ✅ {device_id}: Linked (AccountID: {state.get('AccountID', '')[:20]}...)")
            else:
                all_linked = False
                print(f"   ❌ {device_id}: Not linked")
        else:
            print(f"   ❌ {device_id}: File not found")
            all_linked = False
    
    print(f"\n   Total linked: {linked_count}/10")
    
    if not all_linked:
        print("\n⚠️ Not all devices are linked!")
        response = input("Do you want to continue anyway? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
    
    # Step 2: Close all games
    print("\n2. Closing all games...")
    for i in range(1, 11):
        port = 16800 + (i-1) * 32
        device_ip = f"127.0.0.1:{port}"
        print(f"   Closing game on {device_ip}...")
        try:
            subprocess.run(f"adb -s {device_ip} shell am force-stop com.klab.bleach", 
                          shell=True, capture_output=True, timeout=5)
        except:
            pass
    
    print("   Waiting 2 seconds...")
    await asyncio.sleep(2)
    
    # Step 3: Delete old device files
    print("\n3. Deleting old device files...")
    for i in range(1, 11):
        device_id = f"DEVICE{i}"
        device_file = os.path.join(device_states_dir, f"{device_id}.json")
        if os.path.exists(device_file):
            os.remove(device_file)
            print(f"   Deleted: {device_id}.json")
    
    # Step 4: Fetch new accounts
    print("\n4. Fetching new accounts from Airtable...")
    from airtable_stock_fetcher import check_and_fetch_all_accounts
    
    result = await check_and_fetch_all_accounts()
    
    if result:
        print("\n✅ SUCCESS! New accounts fetched.")
        
        # Step 5: Verify new files
        print("\n5. Verifying new device files...")
        for i in range(1, 11):
            device_id = f"DEVICE{i}"
            device_file = os.path.join(device_states_dir, f"{device_id}.json")
            
            if os.path.exists(device_file):
                with open(device_file, 'r') as f:
                    state = json.load(f)
                email = state.get("Email", "")
                username = state.get("UserName", "")
                reroll = state.get("Reroll_Earse_GameData", 1)
                print(f"   {device_id}: {username} ({email[:20]}...) - Reroll={reroll}")
        
        # Step 6: Check new stock
        stock_file = os.path.join(device_states_dir, "currentlyStock.json")
        if os.path.exists(stock_file):
            with open(stock_file, 'r') as f:
                stock_data = json.load(f)
                print(f"\n   New STOCK number: {stock_data['STOCK']}")
        
        print("\n6. Launching games with reroll tasks...")
        for i in range(1, 11):
            port = 16800 + (i-1) * 32
            device_ip = f"127.0.0.1:{port}"
            print(f"   Launching game on {device_ip}...")
            try:
                subprocess.run(f"adb -s {device_ip} shell monkey -p com.klab.bleach 1", 
                              shell=True, capture_output=True, timeout=5)
            except:
                pass
            await asyncio.sleep(0.5)
        
        print("\n✅ COMPLETE!")
        print("\nThe reroll cycle has been started:")
        print("- All games closed")
        print("- Old accounts deleted")
        print("- New accounts fetched from Airtable")
        print("- All devices set to reroll_erase_gamedata")
        print("- Games relaunched")
        print("\nNow run: python main.py")
        
    else:
        print("\n❌ Failed to fetch accounts from Airtable")
        print("\nPossible issues:")
        print("1. Check your Airtable environment variables")
        print("2. Verify records exist for the current STOCK number")
        print("3. Check network connection")

if __name__ == "__main__":
    asyncio.run(trigger_reroll_now())
