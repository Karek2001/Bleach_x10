# logical_process.py
import asyncio
from actions import execute_tap, find_template_in_region, execute_swipe
from screenrecord_manager import get_screenrecord_manager
import settings

async def run_hard_mode_swipes(device_id):
    """
    Execute smart swipe sequence to find Part-1 HARD template.
    Check for template before and after each swipe, stop when found.
    Maximum 7 swipes if template never appears.
    """
    print(f"\n--- Executing Smart Hard Mode Swipe Sequence on {device_id} ---")
    
    # First check if Part-1 HARD template is already visible
    if settings.SPAM_LOGS:
        print(f"[{device_id}] Checking if Part-1 HARD template is already visible...")
    screenshot = await screenshot_manager.get_screenshot(device_id)
    
    if screenshot is not None:
        part1_hard_pos = await find_template_in_region(
            screenshot,
            "templates/Part1_hard.png",
            [135, 113, 491, 290],  # ROI from task definition
            0.90  # Confidence from task definition
        )
        
        if part1_hard_pos:
            if settings.SPAM_LOGS:
                print(f"[{device_id}] Part-1 HARD template already found at {part1_hard_pos} - no swipes needed!")
            return
    
    # Execute swipes until template is found or max swipes reached
    for i in range(7):
        swipe_num = i + 1
        print(f"[{device_id}] Executing swipe {swipe_num}/7...")
        
        # Execute the swipe: from (0, 270) to (959, 270) with 700ms duration
        await execute_swipe(device_id, 0, 270, 959, 270, 700)
        
        # Wait 2 seconds for content to load
        print(f"[{device_id}] Waiting 2 seconds for content to load...")
        await asyncio.sleep(2)
        
        # Check if Part-1 HARD template is now visible
        if settings.SPAM_LOGS:
            print(f"[{device_id}] Checking for Part-1 HARD template after swipe {swipe_num}...")
        screenshot = await screenshot_manager.get_screenshot(device_id)
        
        if screenshot is not None:
            part1_hard_pos = await find_template_in_region(
                screenshot,
                "templates/Part1_hard.png",
                [135, 113, 491, 290],  # ROI from task definition
                0.85  # Confidence from task definition
            )
            
            if part1_hard_pos:
                if settings.SPAM_LOGS:
                    print(f"[{device_id}] ✅ Part-1 HARD template found at {part1_hard_pos} after {swipe_num} swipe(s)!")
                    print(f"[{device_id}] Smart swipe sequence complete - target found efficiently!")
                return
        else:
            if settings.SPAM_LOGS:
                print(f"[{device_id}] Failed to capture screenshot after swipe {swipe_num}")
    
    if settings.SPAM_LOGS:
        print(f"[{device_id}] ⚠️ Part-1 HARD template not found after 7 swipes - sequence complete")