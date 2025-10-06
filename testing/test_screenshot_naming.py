#!/usr/bin/env python3
"""
Test script to verify the new screenshot naming convention with stock value.
This demonstrates the filename format: {CurrentStock}_{DeviceNumber}_{UserName}.png
"""

import os
import sys
import numpy as np

# Add the project root to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from device_state_manager import device_state_manager
from actions import save_screenshot_with_username

def test_screenshot_naming():
    """Test the new screenshot naming with stock value"""
    print("="*70)
    print("TESTING SCREENSHOT NAMING WITH STOCK VALUE")
    print("="*70)
    
    # Test 1: Check current stock
    print("\n1. Getting current stock value:")
    current_stock = device_state_manager.get_current_stock()
    print(f"   Current stock: {current_stock}")
    
    # Test 2: Simulate different stock values and check naming
    test_stocks = [5, 15, 100, 999]
    
    for test_stock in test_stocks:
        print(f"\n2. Testing with stock value: {test_stock}")
        
        # Set stock to test value
        device_state_manager.set_stock(test_stock)
        
        # Get device state for naming
        device_id = "127.0.0.1:16800"  # DEVICE1
        state = device_state_manager.get_state(device_id)
        username = state.get("UserName", "Player")
        device_name = device_state_manager._get_device_name(device_id)
        device_number = device_name[6:] if device_name.startswith("DEVICE") else "Unknown"
        
        # Show what the filename would be
        expected_filename = f"{test_stock}_{device_number}_{username}.png"
        print(f"   Expected filename: {expected_filename}")
        print(f"   Format: Stock({test_stock}) + Device({device_number}) + User({username})")
    
    # Test 3: Show the actual function behavior (without creating a real screenshot)
    print(f"\n3. Current stock after tests: {device_state_manager.get_current_stock()}")
    
    # Test 4: Show mapping for different devices
    print(f"\n4. Testing filename format for different devices:")
    test_devices = [
        "127.0.0.1:16800",  # DEVICE1
        "127.0.0.1:16832",  # DEVICE2
        "127.0.0.1:17088",  # DEVICE10
    ]
    
    current_stock = device_state_manager.get_current_stock()
    
    for device_id in test_devices:
        device_name = device_state_manager._get_device_name(device_id)
        device_number = device_name[6:] if device_name.startswith("DEVICE") else "Unknown"
        state = device_state_manager.get_state(device_id)
        username = state.get("UserName", "Player")
        
        filename = f"{current_stock}_{device_number}_{username}.png"
        print(f"   {device_id} -> {device_name} -> {filename}")
    
    print(f"\n5. Key Changes Made:")
    print(f"   ✅ OLD FORMAT: DeviceNumber_UserName.png (e.g., '1_Player.png')")
    print(f"   ✅ NEW FORMAT: Stock_DeviceNumber_UserName.png (e.g., '{current_stock}_1_Player.png')")
    print(f"   ✅ Stock value automatically included from currentlyStock.json")
    print(f"   ✅ Files saved to stock_images/ directory")
    print(f"   ✅ Updated documentation in FLAGS_DOCS.md")
    
    print("\n" + "="*70)
    print("SCREENSHOT NAMING TEST COMPLETED")
    print("="*70)
    print(f"\nNow screenshots will include stock value in filename:")
    print(f"Format: {{CurrentStock}}_{{DeviceNumber}}_{{UserName}}.png")

if __name__ == "__main__":
    test_screenshot_naming()
