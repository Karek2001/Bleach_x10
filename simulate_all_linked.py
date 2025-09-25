#!/usr/bin/env python3
"""
Script to simulate all devices being linked and trigger the actual account fetching
This is for demonstration purposes only - it will actually modify device files!
"""

import asyncio
import json
import os
from device_state_manager import device_state_manager
from airtable_stock_fetcher import check_and_fetch_all_accounts

async def simulate_all_linked():
    """Set all devices to isLinked=1 to trigger account fetching"""
    
    print("=" * 60)
    print("SIMULATE ALL DEVICES LINKED - ACTUAL IMPLEMENTATION")
    print("=" * 60)
    print("\nWARNING: This will actually modify your device JSON files!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("Aborted.")
        return
    
    print("\n1. Setting all devices to isLinked=1...")
    for i in range(1, 11):
        device_id = f"DEVICE{i}"
        device_state_manager.update_state(device_id, "isLinked", 1)
        print(f"   {device_id}: isLinked = 1")
    
    print("\n2. Checking current STOCK number...")
    stock_file = os.path.join("device_states", "currentlyStock.json")
    if os.path.exists(stock_file):
        with open(stock_file, 'r') as f:
            stock_data = json.load(f)
            print(f"   Current STOCK: {stock_data['STOCK']}")
    
    print("\n3. Triggering account fetch from Airtable...")
    result = await check_and_fetch_all_accounts()
    
    if result:
        print("\n✅ SUCCESS! Account fetching completed.")
        print("\n4. Verifying new device files...")
        
        # Check a sample device to verify
        device_id = "DEVICE1"
        state = device_state_manager.get_state(device_id)
        
        print(f"\nSample verification for {device_id}:")
        print(f"   Email: {state.get('Email', 'NOT FOUND')}")
        print(f"   UserName: {state.get('UserName', 'NOT FOUND')}")
        print(f"   Password: {'*' * len(state.get('Password', '')) if state.get('Password') else 'NOT FOUND'}")
        print(f"   isLinked: {state.get('isLinked', 'NOT FOUND')}")
        print(f"   CurrentTaskSet: {state.get('CurrentTaskSet', 'NOT FOUND')}")
        
        # Check new stock number
        if os.path.exists(stock_file):
            with open(stock_file, 'r') as f:
                stock_data = json.load(f)
                print(f"\n   New STOCK: {stock_data['STOCK']}")
    else:
        print("\n❌ Account fetching failed or conditions not met.")

if __name__ == "__main__":
    asyncio.run(simulate_all_linked())
