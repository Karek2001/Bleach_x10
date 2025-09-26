# logical_process.py
import asyncio
from actions import execute_tap, find_template_in_region, execute_swipe, ScreenshotManager
from screenrecord_manager import get_screenrecord_manager
import settings

# Initialize screenshot manager
screenshot_manager = ScreenshotManager()

async def handle_game_ready_routing(device_id):
    """
    Handle conditional routing when game is ready to use.
    Use the updated progression logic from device_state_manager.
    """
    from device_state_manager import device_state_manager
    from background_process import monitor
    
    print(f"[{device_id}] Game ready - determining routing...")
    
    # Check if we're currently in a helper task set - if so, don't override it
    current_task_set = getattr(monitor.process_monitor, 'active_task_set', {}).get(device_id, 'main')
    helper_task_sets = ['login2_klab_login', 'login3_wait_for_2fa', 'login4_confirm_link']
    
    if current_task_set in helper_task_sets:
        print(f"[{device_id}] Currently in helper task set '{current_task_set}' - not overriding")
        return
    
    # Use the updated progression logic that handles all completion flags
    recommended_mode = device_state_manager.get_next_task_set_after_restarting(device_id)
    print(f"[{device_id}] Progression logic → {recommended_mode}")
    monitor.process_monitor.set_active_tasks(device_id, recommended_mode)

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

async def run_first_match_script(device_id):
    """
    Execute the First Match tutorial script sequence.
    This is a complex sequence of swipes and taps for the reroll first match tutorial.
    """
    print(f"\n--- Executing First Match Tutorial Script on {device_id} ---")
    
    # Phase 1: 7 swipes to the right
    print(f"[{device_id}] Phase 1: Executing 7 right swipes...")
    for i in range(7):
        await execute_swipe(device_id, 100, 500, 900, 500, 2000)
    
    # 2 second sleep
    print(f"[{device_id}] Waiting 2 seconds...")
    await asyncio.sleep(2)
    
    # Phase 2: 4 taps with 1s between
    print(f"[{device_id}] Phase 2: Executing 4 taps...")
    for i in range(4):
        await execute_tap(device_id, "884,464")
        await asyncio.sleep(1)
    
    # Phase 3: 2 left swipes
    print(f"[{device_id}] Phase 3: Executing 2 left swipes...")
    for i in range(2):
        await execute_swipe(device_id, 900, 380, 100, 380, 2000)
    
    await asyncio.sleep(1)
    
    # Phase 4: 7 taps with 1s between
    print(f"[{device_id}] Phase 4: Executing 7 taps...")
    for i in range(7):
        await execute_tap(device_id, "884,464")
        await asyncio.sleep(1)
    
    # Phase 5: 4 right swipes
    print(f"[{device_id}] Phase 5: Executing 4 right swipes...")
    for i in range(4):
        await execute_swipe(device_id, 100, 500, 900, 500, 2000)
    
    # 4 second sleep
    print(f"[{device_id}] Waiting 4 seconds...")
    await asyncio.sleep(4)
    
    # Phase 6: 2 taps on top-right
    print(f"[{device_id}] Phase 6: Tapping top-right corner twice...")
    for i in range(2):
        await execute_tap(device_id, "901,28")
        await asyncio.sleep(1)
    
    # Phase 7: 2 right swipes with 1s between
    print(f"[{device_id}] Phase 7: Executing 2 right swipes...")
    for i in range(2):
        await execute_swipe(device_id, 100, 500, 900, 500, 2000)
        await asyncio.sleep(1)
    
    # Phase 8: 9 taps with 1s between
    print(f"[{device_id}] Phase 8: Executing 9 taps...")
    for i in range(9):
        await execute_tap(device_id, "884,464")
        if i < 8:  # Don't sleep after the last tap
            await asyncio.sleep(1)
    
    print(f"[{device_id}] ✅ First Match Tutorial Script completed successfully!")