# main.py - Enhanced with clean logging and state tracking
import asyncio
import atexit
import signal
from suppress_warnings import suppress_libpng_warning
suppress_libpng_warning()

from background_process import monitor
from screenrecord_manager import cleanup_all_screenrecord
from logical_process import run_hard_mode_swipes
from device_state_manager import device_state_manager
from actions import run_adb_command

def cleanup_handler(signum=None, frame=None):
    """Clean up screenrecord streaming resources on exit"""
    print("\n🧹 Cleaning up resources...")
    cleanup_all_screenrecord()
    
    # Force kill any remaining ADB/FFmpeg processes
    import subprocess
    try:
        subprocess.run("taskkill /f /im ffmpeg.exe", shell=True, capture_output=True)
    except:
        pass
    
    print("✅ Cleanup complete")

def main():
    """Main entry point for the background monitoring script."""
    # Register cleanup handlers
    atexit.register(cleanup_handler)
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    
    print("🚀 Starting background monitoring...")
    print("📊 Loading device states...")
    
    try:
        # Start continuous monitoring loop with logical task handling
        asyncio.run(run_monitoring_with_logical_tasks())
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user.")
        cleanup_handler()
    except Exception as e:
        print(f"Error occurred: {e}")
        cleanup_handler()
    finally:
        cleanup_handler()

async def optimize_emulators():
    """Apply performance optimizations to all emulators at startup"""
    import settings
    
    optimization_commands = [
        "shell cmd power set-fixed-performance-mode-enabled true",
        "shell settings put global window_animation_scale 0.0",
        "shell settings put global transition_animation_scale 0.0", 
        "shell settings put global animator_duration_scale 0.0",
        "shell settings put system rakuten_denwa 0",
        "shell settings put system send_security_reports 0",
        "shell settings put secure send_action_app_error 0",
        "shell settings put global activity_starts_logging_enabled 0",
        "shell settings put system intelligent_sleep_mode 0",
        "shell settings put secure adaptive_sleep 0",
        "shell settings put global adaptive_battery_management_enabled 0"
    ]
    
    print("⚡ Optimizing all emulators...")
    
    for device_id in settings.DEVICE_IDS:
        print(f"[{device_id}] Applying performance optimizations...")
        for command in optimization_commands:
            try:
                await run_adb_command(command, device_id)
            except Exception as e:
                print(f"[{device_id}] Warning: Failed to execute: {command}")
    
    print("✅ Emulator optimization complete")

async def run_monitoring_with_logical_tasks():
    """Run parallel monitoring for all devices with per-device logical task handling"""
    import settings
    
    # Apply emulator optimizations first
    await optimize_emulators()
    
    # Print initial state summary
    device_state_manager.print_all_device_states()
    
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
                print(f"\n◉ [{triggered_device}] Trigger detected!")
                
                # Get logical task info from monitor
                logical_task_info = getattr(monitor, 'logical_task_info', {})
                task_info = logical_task_info.get(triggered_device, {})
                
                # Only check for and run the hard mode swipe logic
                if task_info.get("HardModeSwipe", False):
                    print(f"[{triggered_device}] Executing Hard Mode swipes...")
                    await run_hard_mode_swipes(triggered_device)
                
                print(f"✓ [{triggered_device}] Logical process complete")
                
                # Clear the logical task info after processing
                if hasattr(monitor, 'logical_task_info') and triggered_device in monitor.logical_task_info:
                    del monitor.logical_task_info[triggered_device]
                    
        except Exception as e:
            print(f"[{device_id}] Monitoring error")
            await asyncio.sleep(1)

if __name__ == '__main__':
    main()