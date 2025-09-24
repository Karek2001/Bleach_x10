#!/usr/bin/env python3
"""
Test script to verify Istanbul timezone functionality in the stock system.
This script demonstrates that timestamps are now in Istanbul/Europe timezone.
"""

import os
import sys
from datetime import datetime
import pytz

# Add the project root to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from device_state_manager import device_state_manager

def test_istanbul_timezone():
    """Test the Istanbul timezone functionality"""
    print("="*70)
    print("TESTING ISTANBUL TIMEZONE FUNCTIONALITY")
    print("="*70)
    
    # Test 1: Show current time in different timezones
    print("\n1. Timezone comparison:")
    
    # System timezone (Germany)
    system_time = datetime.now()
    print(f"   System time (Germany): {system_time.isoformat()}")
    
    # UTC time
    utc_time = datetime.utcnow()
    print(f"   UTC time: {utc_time.isoformat()}")
    
    # Istanbul time
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    istanbul_time = utc_now.astimezone(istanbul_tz)
    print(f"   Istanbul time: {istanbul_time.isoformat()}")
    
    # Our helper method
    our_istanbul_time = device_state_manager._get_istanbul_time()
    print(f"   Our Istanbul time: {our_istanbul_time}")
    
    # Test 2: Test stock system with Istanbul time
    print("\n2. Testing stock system with Istanbul timezone:")
    
    # Delete existing stock file to test auto-generation with new timezone
    stock_file = device_state_manager._get_stock_file_path()
    if os.path.exists(stock_file):
        os.remove(stock_file)
        print("   Deleted existing stock file")
    
    # Get stock (should auto-generate with Istanbul time)
    stock = device_state_manager.get_current_stock()
    print(f"   Current stock: {stock}")
    
    # Increment stock 
    new_stock = device_state_manager.increment_stock("127.0.0.1:16800")
    print(f"   Stock after increment: {new_stock}")
    
    # Test 3: Verify the timestamps in the file
    print("\n3. Verifying timestamps in currentlyStock.json:")
    
    import json
    with open(stock_file, 'r') as f:
        stock_data = json.load(f)
    
    print(f"   Stock value: {stock_data['STOCK']}")
    print(f"   Last updated: {stock_data['LastUpdated']}")
    
    # Parse the timestamp to verify it's Istanbul time
    from dateutil import parser
    try:
        timestamp = parser.parse(stock_data['LastUpdated'])
        print(f"   Parsed timestamp: {timestamp}")
        
        # Check if it includes timezone info
        if timestamp.tzinfo:
            print(f"   Timezone: {timestamp.tzinfo}")
        else:
            print("   No timezone info (should have Istanbul timezone)")
        
    except Exception as e:
        print(f"   Error parsing timestamp: {e}")
    
    # Test 4: Multiple increments to see timestamp updates
    print("\n4. Testing multiple increments with timestamp updates:")
    
    for i in range(3):
        import time
        time.sleep(1)  # Wait a second between increments
        stock = device_state_manager.increment_stock("127.0.0.1:16832")
        
        with open(stock_file, 'r') as f:
            data = json.load(f)
        
        print(f"   Increment {i+1}: Stock={data['STOCK']}, Time={data['LastUpdated']}")
    
    print("\n" + "="*70)
    print("ISTANBUL TIMEZONE TEST COMPLETED")
    print("="*70)
    print("\nNote: All timestamps should now be in Istanbul/Europe timezone")
    print("Even when running this from Germany, the timestamps will be Istanbul time.")

if __name__ == "__main__":
    test_istanbul_timezone()
