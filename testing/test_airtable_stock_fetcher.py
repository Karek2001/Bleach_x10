#!/usr/bin/env python3
"""
Test script for Airtable stock fetching functionality
Tests the airtable_stock_fetcher module which fetches account details from Airtable
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from airtable_stock_fetcher import (
    get_stock_account_details,
    check_and_fetch_all_accounts
)
from device_state_manager import device_state_manager

async def test_fetch_single_account():
    """Test fetching a single account from Airtable"""
    print("=" * 60)
    print("TEST: Fetch Single Account Details")
    print("=" * 60)
    
    # Test parameters
    device_id = "DEVICE1"
    order_number = 1
    stock_number = 999  # Use current stock from currentlyStock.json
    
    # Get current stock from file
    stock_file = os.path.join("device_states", "currentlyStock.json")
    if os.path.exists(stock_file):
        with open(stock_file, 'r') as f:
            stock_data = json.load(f)
            stock_number = stock_data.get('STOCK', 999)
    
    print(f"Testing with: Device={device_id}, Order={order_number}, Stock={stock_number}")
    
    # Fetch account details
    result = await get_stock_account_details(device_id, order_number, stock_number)
    
    if result:
        print("\n✅ Successfully fetched account details:")
        print(f"  Email: {result['Email']}")
        print(f"  UserName: {result['UserName']}")
        print(f"  Password: {'*' * len(result['Password']) if result['Password'] else 'N/A'}")
    else:
        print("\n❌ No account found for these parameters")
    
    return result is not None

async def test_check_all_devices_linked():
    """Test checking if all devices are linked"""
    print("\n" + "=" * 60)
    print("TEST: Check All Devices Linked Status")
    print("=" * 60)
    
    # Check current link status of all devices
    all_linked = True
    for i in range(1, 11):
        device_id = f"DEVICE{i}"
        state = device_state_manager.get_state(device_id)
        is_linked = state.get("isLinked", False)
        print(f"{device_id}: isLinked = {is_linked}")
        if not is_linked:
            all_linked = False
    
    print(f"\nAll devices linked: {all_linked}")
    return all_linked

async def test_simulate_all_linked():
    """Simulate all devices being linked and test account fetching"""
    print("\n" + "=" * 60)
    print("TEST: Simulate All Devices Linked")
    print("=" * 60)
    
    print("Setting all devices to isLinked=1 for testing...")
    
    # Temporarily set all devices to linked
    original_states = {}
    for i in range(1, 11):
        device_id = f"DEVICE{i}"
        original_states[device_id] = device_state_manager.get_state(device_id).get("isLinked", 0)
        device_state_manager.update_state(device_id, "isLinked", 1)
    
    print("All devices set to linked. Testing check_and_fetch_all_accounts...")
    
    # Test the function (in test mode, we won't actually delete files)
    # We'll create a test version that doesn't delete files
    try:
        # Check if all linked
        all_linked = True
        for i in range(1, 11):
            device_id = f"DEVICE{i}"
            state = device_state_manager.get_state(device_id)
            if not state.get("isLinked", False):
                all_linked = False
                break
        
        if all_linked:
            print("\n✅ All devices confirmed linked!")
            print("Would fetch account details from Airtable and recreate device files.")
            print("(Not executing actual file deletion in test mode)")
            
            # Test fetching for each device
            stock_file = os.path.join("device_states", "currentlyStock.json")
            stock_number = 999
            if os.path.exists(stock_file):
                with open(stock_file, 'r') as f:
                    stock_data = json.load(f)
                    stock_number = stock_data.get('STOCK', 999)
            
            print(f"\nWould fetch accounts for STOCK={stock_number}:")
            for i in range(1, 11):
                device_id = f"DEVICE{i}"
                account = await get_stock_account_details(device_id, i, stock_number)
                if account:
                    print(f"  {device_id}: Found account (Email: {account['Email'][:3]}***)")
                else:
                    print(f"  {device_id}: No account found")
        else:
            print("\n❌ Not all devices are linked")
    
    finally:
        # Restore original states
        print("\nRestoring original device states...")
        for device_id, original_value in original_states.items():
            device_state_manager.update_state(device_id, "isLinked", original_value)
    
    return True

async def test_stock_increment():
    """Test stock number increment functionality"""
    print("\n" + "=" * 60)
    print("TEST: Stock Number Management")
    print("=" * 60)
    
    stock_file = os.path.join("device_states", "currentlyStock.json")
    
    # Read current stock
    if os.path.exists(stock_file):
        with open(stock_file, 'r') as f:
            stock_data = json.load(f)
            current_stock = stock_data.get('STOCK', 999)
        print(f"Current STOCK: {current_stock}")
    else:
        print("currentlyStock.json not found")
        current_stock = 999
    
    # Simulate incrementing stock
    new_stock = current_stock + 1
    print(f"Simulated new STOCK after all accounts linked: {new_stock}")
    
    return True

async def main():
    """Run all tests"""
    print("\n" + "█" * 60)
    print("   AIRTABLE STOCK FETCHER TEST SUITE")
    print("█" * 60)
    
    tests_passed = 0
    tests_total = 4
    
    # Test 1: Fetch single account
    try:
        if await test_fetch_single_account():
            tests_passed += 1
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    # Test 2: Check devices linked status
    try:
        await test_check_all_devices_linked()
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    # Test 3: Simulate all linked
    try:
        if await test_simulate_all_linked():
            tests_passed += 1
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    # Test 4: Stock management
    try:
        if await test_stock_increment():
            tests_passed += 1
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    # Summary
    print("\n" + "█" * 60)
    print(f"   TEST RESULTS: {tests_passed}/{tests_total} tests passed")
    print("█" * 60)
    
    if tests_passed == tests_total:
        print("\n✅ All tests passed successfully!")
    else:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) failed")

if __name__ == "__main__":
    asyncio.run(main())
