#!/usr/bin/env python3
"""
Test script for Pixel-OneOrMoreMatched functionality
"""
import asyncio
import numpy as np
from actions import batch_check_pixels_enhanced, hex_to_rgb

def create_test_screenshot():
    """Create a test screenshot with known pixel values"""
    # Create a 1000x1000 RGB image
    img = np.zeros((1000, 1000, 3), dtype=np.uint8)
    
    # Set specific pixels to known colors
    img[180, 218] = hex_to_rgb("#fefefe")  # 218,180 -> #fefefe
    img[221, 478] = hex_to_rgb("#f6f4f6")  # 478,221 -> #f6f4f6  
    img[198, 746] = hex_to_rgb("#d6c6ce")  # 746,198 -> #d6c6ce
    img[406, 439] = hex_to_rgb("#fec46c")  # 439,406 -> #fec46c
    
    return img

async def test_pixel_one_or_more_matched():
    """Test the Pixel-OneOrMoreMatched functionality"""
    print("Testing Pixel-OneOrMoreMatched functionality...")
    
    # Create test screenshot
    test_screenshot = create_test_screenshot()
    
    # Test case 1: Should match on second consecutive pair (478,221 + 746,198)
    test_task_1 = {
        "task_name": "Test Match Found",
        "type": "Pixel-OneOrMoreMatched", 
        "pixel-values": ["218,180", "#fefefe", "478,221", "#f6f4f6", "746,198", "#d6c6ce", "439,406", "#fec46c"],
        "click_location_str": "694,189",
        "priority": 20,
        "cooldown": 2.0,
    }
    
    # Test case 2: Should not match (wrong colors)
    test_task_2 = {
        "task_name": "Test No Match",
        "type": "Pixel-OneOrMoreMatched",
        "pixel-values": ["218,180", "#000000", "478,221", "#111111", "746,198", "#222222", "439,406", "#333333"],
        "click_location_str": "694,189", 
        "priority": 20,
        "cooldown": 2.0,
    }
    
    # Test case 3: Should match on first consecutive pair (218,180 + 478,221)
    test_task_3 = {
        "task_name": "Test First Pair Match",
        "type": "Pixel-OneOrMoreMatched",
        "pixel-values": ["218,180", "#fefefe", "478,221", "#f6f4f6", "999,999", "#000000", "888,888", "#111111"],
        "click_location_str": "694,189",
        "priority": 20,
        "cooldown": 2.0,
    }
    
    tasks = [test_task_1, test_task_2, test_task_3]
    
    # Test with fake device_id
    device_id = "test_device"
    
    try:
        # Call the enhanced batch check function with our test screenshot
        matched_tasks = await batch_check_pixels_enhanced(device_id, tasks, test_screenshot)
        
        print(f"\nResults:")
        print(f"Total tasks tested: {len(tasks)}")
        print(f"Matched tasks: {len(matched_tasks)}")
        
        for task in matched_tasks:
            print(f"✓ Matched: {task['task_name']}")
        
        # Expected results: task_1 and task_3 should match, task_2 should not
        expected_matches = ["Test Match Found", "Test First Pair Match"]
        actual_matches = [task['task_name'] for task in matched_tasks]
        
        if set(expected_matches) == set(actual_matches):
            print(f"\n✅ TEST PASSED: Expected matches found")
            return True
        else:
            print(f"\n❌ TEST FAILED:")
            print(f"Expected: {expected_matches}")
            print(f"Actual: {actual_matches}")
            return False
            
    except Exception as e:
        print(f"❌ TEST ERROR: {e}")
        return False

async def main():
    """Main test function"""
    print("=" * 50)
    print("Testing Pixel-OneOrMoreMatched Implementation")
    print("=" * 50)
    
    success = await test_pixel_one_or_more_matched()
    
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n💥 Tests failed!")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
