# main.py
import asyncio
import atexit
import signal
from background_process import continuous_pixel_watch, monitor
from screenrecord_manager import cleanup_all_screenrecord
from logical_process import run_hard_mode_swipes # <-- FIXED: Removed 'run_logical_tasks'

def cleanup_handler(signum=None, frame=None):
    """Clean up screenrecord streaming resources on exit"""
    print("\n🧹 Cleaning up screenrecord resources...")
    cleanup_all_screenrecord()
    
    # Force kill any remaining ADB/FFmpeg processes
    import subprocess
    try:
        subprocess.run("taskkill /f /im ffmpeg.exe", shell=True, capture_output=True)
        print("🔪 Force-killed remaining processes")
    except:
        pass
    
    print("✅ Cleanup complete")

def main():
    """
    Main entry point for the background monitoring script.
    """
    # Register cleanup handlers
    atexit.register(cleanup_handler)
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    
    print("🚀 Starting background monitoring...")
    try:
        # Start continuous monitoring loop with logical task handling
        asyncio.run(run_monitoring_with_logical_tasks())
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user.")
        cleanup_handler()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        cleanup_handler()
    finally:
        cleanup_handler()

async def run_monitoring_with_logical_tasks():
    """Run parallel monitoring for all devices with per-device logical task handling"""
    import settings
    
    # Create monitoring tasks for each device
    device_tasks = []
    for device_id in settings.DEVICE_IDS:
        task = asyncio.create_task(monitor_single_device_with_logical_tasks(device_id))
        device_tasks.append(task)
    
    try:
        # Run all device monitoring in parallel
        await asyncio.gather(*device_tasks)
    except Exception as e:
        print(f"Error in parallel monitoring: {e}")
        # Cancel all tasks on error
        for task in device_tasks:
            if not task.done():
                task.cancel()

async def monitor_single_device_with_logical_tasks(device_id: str):
    """Monitor a single device and handle its logical tasks independently"""
    while True:
        try:
            # Monitor this specific device for logical tasks
            triggered_device = await monitor.watch_device_optimized(device_id)
            
            if triggered_device:
                print(f"\n❗ [{triggered_device}] Trigger detected! Switching to logical process...")
                
                # Get logical task info from monitor
                logical_task_info = getattr(monitor, 'logical_task_info', {})
                task_info = logical_task_info.get(triggered_device, {})
                
                print(f"[{triggered_device}] DEBUG: Logical task info: {task_info}")
                
                # --- LOGIC UPDATED HERE ---
                # Only check for and run the hard mode swipe logic
                if task_info.get("HardModeSwipe", False):
                    print(f"[{triggered_device}] Hard Mode detected - executing swipe sequence...")
                    await run_hard_mode_swipes(triggered_device)
                
                print(f"👍 [{triggered_device}] Logical process finished. Continuing monitoring...")
                
                # Clear the logical task info after processing
                if hasattr(monitor, 'logical_task_info') and triggered_device in monitor.logical_task_info:
                    del monitor.logical_task_info[triggered_device]
                    
        except Exception as e:
            print(f"[{device_id}] Error in device monitoring: {e}")
            await asyncio.sleep(1)

if __name__ == '__main__':
    main()