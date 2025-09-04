#!/usr/bin/env python3
"""
Debug script to test Stars template matching with FullyAnylaze flag
"""

import cv2
import numpy as np
import os
import sys
from actions import template_cache, find_all_template_matches_force
import asyncio

async def debug_stars_template():
    """Test the Stars template matching specifically"""
    
    # Load a screenshot for testing (you'll need to provide this)
    screenshot_path = "screenshot_debug.png"  # You can take a screenshot and save it here
    
    if not os.path.exists(screenshot_path):
        print(f"Please take a screenshot and save it as '{screenshot_path}' for debugging")
        print("You can use: adb shell screencap -p | sed 's/\\r$//' > screenshot_debug.png")
        return
    
    # Load screenshot
    screenshot = cv2.imread(screenshot_path)
    if screenshot is None:
        print(f"Failed to load screenshot: {screenshot_path}")
        return
    
    # Convert BGR to RGB (same as runtime)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
    
    print(f"Screenshot loaded: {screenshot.shape}")
    
    # Test parameters from your task
    template_path = "templates/Stars.png"
    roi = [3, 86, 953, 415]  # Your current ROI
    confidence = 0.60  # Your current confidence
    
    print(f"Testing template: {template_path}")
    print(f"ROI: {roi}")
    print(f"Confidence: {confidence}")
    
    # Test template loading
    template = template_cache.get_template(template_path)
    if template is None:
        print(f"FAILED: Could not load template {template_path}")
        return
    
    print(f"Template loaded successfully: {template.shape}")
    
    # Test ROI extraction
    x, y, w, h = roi
    if y + h > screenshot.shape[0] or x + w > screenshot.shape[1]:
        print(f"WARNING: ROI exceeds screenshot bounds!")
        print(f"Screenshot: {screenshot.shape[:2]}, ROI end: ({x+w}, {y+h})")
    
    roi_img = screenshot[y:y+h, x:x+w]
    print(f"ROI extracted: {roi_img.shape}")
    
    # Test template matching manually
    result = cv2.matchTemplate(roi_img.astype(np.uint8), 
                              template.astype(np.uint8), 
                              cv2.TM_CCOEFF_NORMED)
    
    max_val = np.max(result)
    min_val = np.min(result)
    print(f"Template matching result - Min: {min_val:.3f}, Max: {max_val:.3f}")
    print(f"Looking for confidence >= {confidence}")
    
    # Find locations above threshold
    locations = np.where(result >= confidence)
    print(f"Matches found above {confidence}: {len(locations[0])}")
    
    if len(locations[0]) == 0:
        print("No matches found!")
        print("Try these solutions:")
        print(f"1. Lower confidence (current max confidence is {max_val:.3f})")
        print("2. Check if ROI covers the star locations")
        print("3. Verify template image is correct")
        
        # Show some confidence values at different thresholds
        for test_conf in [0.5, 0.4, 0.3, 0.2]:
            test_locations = np.where(result >= test_conf)
            print(f"   At confidence {test_conf}: {len(test_locations[0])} matches")
    else:
        print(f"SUCCESS: Found {len(locations[0])} potential matches")
        
        # Test the full function
        matches = await find_all_template_matches_force(screenshot, template_path, roi, confidence)
        print(f"find_all_template_matches_force returned: {len(matches)} matches")
        
        for i, (x, y) in enumerate(matches):
            print(f"  Match {i+1}: ({x}, {y})")

if __name__ == "__main__":
    asyncio.run(debug_stars_template())
