#!/usr/bin/env python3
"""
Test script for template matching functionality
"""
import asyncio
import numpy as np
from actions import batch_check_pixels, screenshot_manager, template_cache

async def test_template_matching():
    """Test template matching with sample tasks"""
    
    # Sample device ID (replace with your actual device)
    device_id = "emulator-5554"  # Change this to your device ID
    
    # Example tasks combining both pixel and template matching
    test_tasks = [
        # Pixel-based task (backward compatible)
        {
            "task_name": "Test Pixel Search",
            "type": "pixel",
            "click_location_str": "500,900",
            "search_array": ["100,100","#ffffff", "101,100","#ffffff"],  # White pixels
            "isLogical": False,
            "NeedRestart": False,
        },
        
        # Template matching task with fixed click position
        {
            "task_name": "Test Template Search",
            "type": "template",
            "template_path": "templates/Test/test_button.png",  # You'll need to create this
            "roi": [200, 400, 400, 300],  # Search in region x=200, y=400, width=400, height=300
            "confidence": 0.8,  # 80% match confidence
            "click_location_str": "400,550",  # Fixed click position
            "use_match_position": False,
            "isLogical": False,
            "NeedRestart": False,
        },
        
        # Template matching with dynamic click (clicks on found template)
        {
            "task_name": "Test Dynamic Template Click",
            "type": "template",
            "template_path": "templates/Test/dynamic_target.png",
            "roi": [0, 0, 1080, 1920],  # Full screen search
            "confidence": 0.6,  # Lower confidence for animated/changing elements
            "use_match_position": True,  # Click at center of matched template
            "isLogical": True,
            "NeedRestart": False,
        },
    ]
    
    print("Starting template matching test...")
    print(f"Testing with device: {device_id}")
    
    # Get a screenshot
    print("\nCapturing screenshot...")
    screenshot = await screenshot_manager.get_screenshot(device_id)
    
    if screenshot is None:
        print("Failed to capture screenshot. Make sure device is connected.")
        return
    
    print(f"Screenshot captured: {screenshot.shape}")
    
    # Test batch checking with mixed task types
    print("\nTesting batch_check_pixels with mixed task types...")
    matched_tasks = await batch_check_pixels(device_id, test_tasks, screenshot)
    
    if matched_tasks:
        print(f"\nMatched {len(matched_tasks)} tasks:")
        for task in matched_tasks:
            print(f"  - {task['task_name']} (type: {task.get('type', 'pixel')})")
            print(f"    Click location: {task['click_location_str']}")
    else:
        print("\nNo tasks matched.")
    
    # Show template cache info
    print(f"\nTemplate cache size: {len(template_cache.templates)}")
    for path in template_cache.templates.keys():
        print(f"  - Cached: {path}")

async def create_sample_template():
    """Create a sample template image for testing"""
    import cv2
    import os
    
    # Create templates directory if it doesn't exist
    os.makedirs("templates", exist_ok=True)
    
    # Create a simple test button image (50x30 pixels)
    button = np.ones((30, 50, 3), dtype=np.uint8) * 255  # White background
    cv2.rectangle(button, (2, 2), (47, 27), (0, 128, 255), 2)  # Orange border
    cv2.putText(button, "TEST", (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    # Save as template
    cv2.imwrite("templates/Test/test_button.png", cv2.cvtColor(button, cv2.COLOR_RGB2BGR))
    print("Created sample template: templates/Test/test_button.png")
    
    # Create a dynamic target template (circle)
    target = np.zeros((40, 40, 3), dtype=np.uint8)
    cv2.circle(target, (20, 20), 18, (255, 0, 0), -1)  # Red circle
    cv2.circle(target, (20, 20), 12, (255, 255, 255), -1)  # White center
    cv2.circle(target, (20, 20), 6, (255, 0, 0), -1)  # Red bullseye
    
    cv2.imwrite("templates/Test/dynamic_target.png", cv2.cvtColor(target, cv2.COLOR_RGB2BGR))
    print("Created sample template: templates/Test/dynamic_target.png")

async def main():
    """Main test function"""
    print("=== Template Matching Test Suite ===\n")
    
    # Create sample templates
    await create_sample_template()
    
    # Run template matching test
    await test_template_matching()
    
    print("\n=== Test Complete ===")
    print("\nUsage in BACKGROUND_TASKS:")
    print("""
    # For pixel-based search (existing method):
    {
        "task_name": "Your Task Name",
        "type": "pixel",  # or omit for backward compatibility
        "click_location_str": "x,y",
        "search_array": ["x1,y1","#hexcolor", ...],
        "isLogical": False,
        "NeedRestart": False,
    }
    
    # For template matching:
    {
        "task_name": "Your Task Name",
        "type": "template",
        "template_path": "path/to/template.png",
        "roi": [x, y, width, height],  # Region to search in
        "confidence": 0.75,  # 0.0 to 1.0 (lower for animated elements)
        "click_location_str": "x,y",  # Fixed click position
        "use_match_position": False,  # Set True to click on found template
        "isLogical": False,
        "NeedRestart": False,
    }
    """)

if __name__ == "__main__":
    asyncio.run(main())
