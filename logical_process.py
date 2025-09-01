# logical_process.py
import asyncio
# Import the function from its new central location
from actions import search_pixels_and_click

async def run_logical_tasks(device_id):
    """
    A sequence of specific tasks to run AFTER the background trigger is found.
    """
    print(f"\n--- Executing Logic on {device_id} ---")
    
    # --- Example Task 1: Find a confirmation button and click it ---
    await search_pixels_and_click(
        device_id=device_id,
        click_location_str="270,900", # "OK" button coordinates
        search_array=[
            "270,900", "#2ecc71",
            "275,905", "#27ae60"
        ]
        # isLogical defaults to False, which is what we want here.
    )
    
    print(f"[{device_id}] Waiting for 2 seconds for the next screen...")
    await asyncio.sleep(2)
    
    # --- Example Task 2: Find a different screen and perform another action ---
    await search_pixels_and_click(
        device_id=device_id,
        click_location_str="450,150", # "Close" button coordinates
        search_array=[
            "450,150", "#e74c3c"
        ]
    )
    
    print(f"[{device_id}] Logic sequence complete.")