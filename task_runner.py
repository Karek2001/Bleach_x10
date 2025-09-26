# task_runner.py
import asyncio
import os
from datetime import datetime
import settings

# Import from our actions file and other modules
from actions import run_adb_command
from logical_process import run_logical_tasks, run_hard_mode_swipes, run_first_match_script
# Import the monitor instance directly to run it per-device
from background_process import monitor

# --- Logging Functions ---
def log_stock_completion(stock_number: int):
    """Logs when a stock is completed to logs.txt file."""
    current_time = datetime.now().strftime("%H:%M")
    log_message = f"STOCK #{stock_number} FINISHED AT {current_time}\n"
    
    try:
        with open("logs.txt", "a", encoding="utf-8") as log_file:
            log_file.write(log_message)
        print(f"📝 Logged completion: {log_message.strip()}")
    except Exception as e:
        print(f"❌ Error writing to logs.txt: {e}")

# --- Stock and Game Management (Orchestration Level) ---
async def import_stock_for_device(device_id, device_index, stock_number):
    """Imports the correct stock file for a single device with added delays for stability."""
    print(f"Processing Device #{device_index} ({device_id}) with Stock #{stock_number}...")
    
    # 1. Delete old files
    print(f"  -> Deleting old files for device {device_index}...")
    for file_key in settings.ECD_FILES:
        remote_path = f"{settings.REMOTE_DATA_DIR}/{settings.ECD_FILES[file_key]}"
        await run_adb_command(f"shell rm -f {remote_path}", device_id)
    
    await asyncio.sleep(1.0)

    # 2. Push new ECD file
    stock_folder = os.path.join(settings.LOCAL_STOCKS_PATH_BASE, str(stock_number), str(device_index))
    local_ecd_path = os.path.join(stock_folder, settings.ECD_FILES['PRIMARY'])
    
    if not os.path.exists(local_ecd_path):
        print(f"  -> ❌ Error: ECD file not found for device {device_index} at {local_ecd_path}")
        return False
        
    print(f"  -> Pushing new stock file for device {device_index}...")
    remote_ecd_path = f"{settings.REMOTE_DATA_DIR}/{settings.ECD_FILES['PRIMARY']}"
    await run_adb_command(f"push \"{local_ecd_path}\" \"{remote_ecd_path}\"", device_id)
    
    await asyncio.sleep(1.0)
    
    print(f"  -> ✅ Successfully pushed stock for device {device_index}.")
    return True

# --- Game Lifecycle Functions ---
async def launch_game(device_id):
    """Launches the game on the specified device using the monkey command."""
    command = f"shell monkey -p {settings.GAME_PACKAGE_NAME} -c android.intent.category.LAUNCHER 1"
    await run_adb_command(command, device_id)

async def kill_game(device_id):
    """Kills the game process on the specified device."""
    await run_adb_command(f"shell am force-stop {settings.GAME_PACKAGE_NAME}", device_id)

# --- NEW: Independent Device Automation Cycle ---
async def run_full_cycle_for_device(device_id: str):
    """Launches, monitors, and processes logical tasks for a single, independent device."""
    print(f"🚀 [{device_id}] Starting full automation cycle.")
    
    # 1. Launch the game on this device
    await launch_game(device_id)
    await asyncio.sleep(2) # Give the game a moment to start

    # 2. Enter the monitoring phase for this specific device.
    # This function will now wait until this specific device finds its logical trigger.
    print(f"🧐 [{device_id}] Entering background monitoring...")
    triggered_device = await monitor.watch_device_optimized(device_id)

    # 3. If a logical trigger was found, run the sequence and clean up.
    if triggered_device:
        print(f"\n❗ [{device_id}] Trigger detected! Switching to logical process...")
        
        # Check if this is a hard mode swipe task
        logical_task_info = getattr(monitor, 'logical_task_info', {})
        task_info = logical_task_info.get(triggered_device, {})
        
        print(f"[{triggered_device}] DEBUG: Logical task info: {task_info}")
        
        if task_info.get("HardModeSwipe", False):
            print(f"[{triggered_device}] Hard Mode detected - executing swipe sequence...")
            await run_hard_mode_swipes(triggered_device)
        elif task_info.get("First_Match_Script", False):
            print(f"[{triggered_device}] First Match detected - executing tutorial script...")
            await run_first_match_script(triggered_device)
        else:
            # Default logical task (clear story logic)
            print(f"[{triggered_device}] Running default logical tasks...")
            await run_logical_tasks(triggered_device)
        
        print(f"👍 [{device_id}] Logical process finished. Killing game.")
        await kill_game(triggered_device)
    else:
        # This can happen if monitoring is interrupted (e.g., by Ctrl+C)
        print(f"🛑 [{device_id}] Monitoring stopped without a trigger. Killing game.")
        await kill_game(device_id)

# --- REVISED: Main Orchestration Loop ---
async def process_stocks(stocks_to_process: list[int]):
    """Orchestrates the automation for a list of stocks, running devices in parallel."""
    
    for stock_number in stocks_to_process:
        print(f"\n--- ⚙️ Starting Cycle with Stock #{stock_number} ⚙️ ---")
        
        # STEP 1: Prepare all devices by importing the correct stock files.
        import_tasks = [
            import_stock_for_device(dev_id, i + 1, stock_number)
            for i, dev_id in enumerate(settings.DEVICE_IDS)
        ]
        results = await asyncio.gather(*import_tasks)

        if not all(results):
            print(f"⚠️ Error importing stock #{stock_number}. Skipping to the next stock.")
            continue
        
        print(f"\n✅ Stock #{stock_number} import complete for all devices.")
        print("🚀 Starting parallel automation cycles for all devices...")
        
        # STEP 2: Run the full, independent automation cycle for each device concurrently.
        # asyncio.gather will wait for ALL devices to finish their tasks before proceeding.
        device_tasks = [
            run_full_cycle_for_device(dev_id) 
            for dev_id in settings.DEVICE_IDS
        ]
        await asyncio.gather(*device_tasks)

        print(f"\n--- ✅ All devices finished processing Stock #{stock_number} ✅ ---")
        
        # Log the completion of this stock
        log_stock_completion(stock_number)
    
    print("\n🎉 --- All selected stocks have been processed. Automation finished. ---")