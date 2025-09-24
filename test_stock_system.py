#!/usr/bin/env python3
"""
Test script for the stock management system.
This script demonstrates the auto-generation and increment functionality.
"""

import os
import sys
import json

# Add the project root to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from device_state_manager import device_state_manager

def test_stock_system():
    """Test the stock management system functionality"""
    print("="*60)
    print("TESTING STOCK MANAGEMENT SYSTEM")
    print("="*60)
    
    # Test 1: Check current stock
    print("\n1. Getting current stock value:")
    current_stock = device_state_manager.get_current_stock()
    print(f"   Current stock: {current_stock}")
    
    # Test 2: Increment stock
    print("\n2. Testing increment_stock functionality:")
    new_stock = device_state_manager.increment_stock("127.0.0.1:16800")
    print(f"   Stock after increment: {new_stock}")
    
    # Test 3: Increment again
    print("\n3. Incrementing again:")
    newer_stock = device_state_manager.increment_stock("127.0.0.1:16832")
    print(f"   Stock after second increment: {newer_stock}")
    
    # Test 4: Delete file and test auto-generation
    print("\n4. Testing auto-generation when file is deleted:")
    stock_file = device_state_manager._get_stock_file_path()
    print(f"   Stock file path: {stock_file}")
    
    if os.path.exists(stock_file):
        print("   Deleting stock file...")
        os.remove(stock_file)
        print("   File deleted!")
    
    print("   Attempting to get stock value (should auto-generate):")
    restored_stock = device_state_manager.get_current_stock()
    print(f"   Stock value after auto-generation: {restored_stock}")
    
    # Test 5: Verify file was recreated
    print("\n5. Verifying file recreation:")
    if os.path.exists(stock_file):
        print("   ✅ File successfully recreated!")
        with open(stock_file, 'r') as f:
            data = json.load(f)
        print(f"   File contents: {data}")
    else:
        print("   ❌ File was not recreated!")
    
    # Test 6: Set stock to specific value
    print("\n6. Testing set_stock functionality:")
    set_stock = device_state_manager.set_stock(10, "127.0.0.1:16864")
    print(f"   Stock set to: {set_stock}")
    
    print("\n" + "="*60)
    print("STOCK SYSTEM TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    test_stock_system()
