# logical_process.py
import asyncio
# Import the functions from actions
from actions import search_pixels_and_click, screenshot_manager, find_template_in_region, execute_tap

async def run_logical_tasks(device_id):
    """
    A sequence of specific tasks to run AFTER the background trigger is found.
    Handles the Clear word -> Arrow check -> Menu click logic
    """
    print(f"\n--- Executing Clear Story Logic on {device_id} ---")
    
    # Wait 5 seconds after detecting Clear word
    print(f"[{device_id}] Clear word detected! Waiting 5 seconds...")
    await asyncio.sleep(5)
    
    # Check for NextStories arrow
    print(f"[{device_id}] Checking for NextStories arrow...")
    screenshot = await screenshot_manager.get_screenshot(device_id)
    
    if screenshot is not None:
        # Check for arrow using the same template and ROI as the original task
        arrow_pos = await find_template_in_region(
            screenshot, 
            "templates/NextStories.png",
            [856, 206, 102, 107],  # Same ROI as original arrow task
            0.70  # Same confidence as original arrow task
        )
        
        if arrow_pos:
            print(f"[{device_id}] Arrow found at {arrow_pos} - no action needed, story progression available")
        else:
            print(f"[{device_id}] No arrow found - clicking menu button at 72,472")
            await execute_tap(device_id, "72,472")
    else:
        print(f"[{device_id}] Failed to capture screenshot, clicking menu button as fallback")
        await execute_tap(device_id, "72,472")
    
    print(f"[{device_id}] Clear story logic sequence complete.")