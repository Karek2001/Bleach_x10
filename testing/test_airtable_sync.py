#!/usr/bin/env python3
# test_airtable_sync.py - Test Airtable synchronization functionality

import json
import os
import sys
from airtable_sync import sync_device_to_airtable, calculate_price_from_orbs
from device_state_manager import device_state_manager

def test_price_calculation():
    """Test the price calculation logic"""
    print("🧪 Testing price calculation logic...")
    
    test_cases = [
        ("20,102", 9.99),
        ("21,122", 9.99), 
        ("22,935", 10.99),
        ("23,445", 10.99),
        ("19,999", 0.00),
        ("24,000", 0.00),
        ("", 0.00),
        ("abc", 0.00)
    ]
    
    for orbs_str, expected_price in test_cases:
        calculated_price = calculate_price_from_orbs(orbs_str)
        status = "✅" if calculated_price == expected_price else "❌"
        print(f"  {status} Orbs: '{orbs_str}' → Price: ${calculated_price} (expected: ${expected_price})")
    
    print()

def load_test_device_data():
    """Load the test device data"""
    test_file = "/home/karek/Downloads/shared/Bleach_10x/device_test.json"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return None
        
    try:
        with open(test_file, 'r') as f:
            data = json.load(f)
            print(f"✅ Loaded test device data from {test_file}")
            return data
    except Exception as e:
        print(f"❌ Error loading test file: {e}")
        return None

def simulate_device_state():
    """Simulate device state with test data"""
    test_data = load_test_device_data()
    if not test_data:
        return False
        
    # Temporarily override device state for testing
    test_device_id = "127.0.0.1:17056"
    
    # Save current state if it exists
    original_state = None
    try:
        original_state = device_state_manager.get_state(test_device_id)
    except:
        pass
    
    # Set test data
    for key, value in test_data.items():
        device_state_manager.update_state(test_device_id, key, value)
    
    print(f"📝 Set test device state for {test_device_id}")
    print(f"   Email: {test_data.get('Email', 'N/A')}")
    print(f"   AccountID: {test_data.get('AccountID', 'N/A')}")
    print(f"   Orbs: {test_data.get('Orbs', 'N/A')}")
    print(f"   isLinked: {test_data.get('isLinked', 'N/A')}")
    
    return test_device_id

def test_airtable_sync_dry_run():
    """Test the Airtable sync without actually calling the API"""
    print("🧪 Testing Airtable sync logic (dry run)...")
    
    device_id = simulate_device_state()
    if not device_id:
        return False
        
    device_data = device_state_manager.get_state(device_id)
    email = device_data.get("Email", "")
    orbs = device_data.get("Orbs", "0")
    
    if not email:
        print("❌ No email found in test data")
        return False
        
    print(f"📧 Email to search: {email}")
    print(f"💎 Orbs value: {orbs}")
    
    # Test price calculation
    calculated_price = calculate_price_from_orbs(orbs)
    print(f"💰 Calculated price: ${calculated_price}")
    
    # Prepare the data that would be sent to Airtable
    is_linked = device_data.get("isLinked", False)
    if isinstance(is_linked, str):
        is_linked = is_linked.lower() == "true"
    elif isinstance(is_linked, int):
        is_linked = bool(is_linked)
    
    airtable_data = {
        "isLinked": is_linked,
        "AccountID": str(device_data.get("AccountID", "")),
        "UserName": str(device_data.get("UserName", "Player")),
        "Orbs": str(orbs),
        "Price": calculated_price
    }
    
    print(f"📊 Data prepared for Airtable:")
    for key, value in airtable_data.items():
        print(f"   {key}: {value} ({type(value).__name__})")
    
    return True

def test_full_airtable_sync():
    """Test the full Airtable sync (REAL API CALL)"""
    print("🚨 WARNING: This will make a REAL API call to Airtable!")
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    if response != "yes":
        print("⏸️  Full sync test cancelled")
        return False
        
    print("🔄 Running full Airtable sync test...")
    
    device_id = simulate_device_state()
    if not device_id:
        return False
        
    # Run the actual sync
    success = sync_device_to_airtable(device_id)
    
    if success:
        print("✅ Airtable sync test completed successfully!")
        
        # Check if synced flag was set
        updated_state = device_state_manager.get_state(device_id)
        synced_flag = updated_state.get("synced_to_airtable", False)
        if synced_flag:
            print("✅ synced_to_airtable flag set correctly")
        else:
            print("❌ synced_to_airtable flag not set")
            
    else:
        print("❌ Airtable sync test failed")
        
    return success

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 AIRTABLE SYNC TEST SUITE")
    print("=" * 60)
    
    # Test 1: Price calculation
    test_price_calculation()
    
    # Test 2: Dry run
    print("📋 Test 2: Dry Run (No API calls)")
    if test_airtable_sync_dry_run():
        print("✅ Dry run test passed\n")
    else:
        print("❌ Dry run test failed\n")
        return
    
    # Test 3: Full sync (optional)
    print("📋 Test 3: Full Airtable Sync (Real API call)")
    test_full_airtable_sync()
    
    print("\n" + "=" * 60)
    print("🏁 Test suite completed")
    print("=" * 60)

if __name__ == "__main__":
    main()
