# main.py - Enhanced with Telegram bot integration
import asyncio
import atexit
import signal
import sys
import traceback

# Try to suppress warnings, but handle errors gracefully
try:
    from suppress_warnings import suppress_libpng_warning
    suppress_libpng_warning()
except Exception as e:
    print(f"Warning: Could not suppress warnings: {e}")

try:
    from background_process import monitor
    from screenrecord_manager import cleanup_all_screenrecord
    from logical_process import run_hard_mode_swipes, handle_game_ready_routing, run_first_match_script
    from device_state_manager import device_state_manager
    from actions import run_adb_command
    from device_status_bot import DeviceStatusBot  # Import the telegram bot
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nPlease make sure all required modules are present and installed.")
    print("Run: pip install -r requirements.txt")
    traceback.print_exc()
    sys.exit(1)

# Global bot instance
telegram_bot = None
bot_task = None

def cleanup_handler(signum=None, frame=None):
    """Clean up resources on exit"""
    global bot_task
    
    print("\n🧹 Cleaning up resources...")
    cleanup_all_screenrecord()
    
    # Cancel bot task if running
    if bot_task and not bot_task.done():
        bot_task.cancel()
    
    # Force kill any remaining ADB/FFmpeg processes
    import subprocess
    try:
        if sys.platform == "win32":
            subprocess.run("taskkill /f /im ffmpeg.exe", shell=True, capture_output=True)
        else:
            subprocess.run("pkill ffmpeg", shell=True, capture_output=True)
    except:
        pass
    
    print("✅ Cleanup complete")

async def start_telegram_bot():
    """Start the telegram bot in the background"""
    global telegram_bot
    
    # Bot configuration
    BOT_TOKEN = "8249078165:AAHcRuIdR4DGDUpMUJz7EEoC6GEt-CFMvB4"
    CHAT_ID = "-1001324257791"
    THREAD_ID = 28415
    
    print("📱 Starting Telegram bot...")
    telegram_bot = DeviceStatusBot(BOT_TOKEN, CHAT_ID, THREAD_ID)
    
    try:
        await telegram_bot.run_bot()
    except Exception as e:
        print(f"⚠️ Telegram bot error: {e}")

async def optimize_emulators():
    """Apply performance optimizations to all emulators at startup"""
    import settings
    
    optimization_commands = [
        "shell cmd power set-fixed-performance-mode-enabled true",
        "shell settings put global window_animation_scale 0.0",
        "shell settings put global transition_animation_scale 0.0", 
        "shell settings put global animator_duration_scale 0.0",
    ]
    
    print("⚡ Optimizing all emulators...")
    
    for device_id in settings.DEVICE_IDS:
        print(f"[{device_id}] Applying performance optimizations...")
        for command in optimization_commands:
            try:
                await run_adb_command(command, device_id)
            except Exception:
                pass
    
    print("✅ Emulator optimization complete")

async def monitor_single_device_with_logical_tasks(device_id: str):
    """Monitor a single device and handle its logical tasks independently"""
    while True:
        try:
            triggered_device = await monitor.watch_device_optimized(device_id)
            
            if triggered_device:
                print(f"\n◉ [{triggered_device}] Trigger detected!")
                
                logical_task_info = getattr(monitor, 'logical_task_info', {})
                task_info = logical_task_info.get(triggered_device, {})
                
                if task_info.get("HardModeSwipe", False):
                    print(f"[{triggered_device}] Executing Hard Mode swipes...")
                    await run_hard_mode_swipes(triggered_device)
                elif task_info.get("First_Match_Script", False):
                    print(f"[{triggered_device}] Executing First Match tutorial script...")
                    await run_first_match_script(triggered_device)
                elif "Game Opened Ready To Use" in task_info.get("task_name", ""):
                    print(f"[{triggered_device}] Handling game ready routing...")
                    await handle_game_ready_routing(triggered_device)
                
                print(f"✓ [{triggered_device}] Logical process complete")
                
                if hasattr(monitor, 'logical_task_info') and triggered_device in monitor.logical_task_info:
                    del monitor.logical_task_info[triggered_device]
                    
        except Exception as e:
            print(f"[{device_id}] Monitoring error")
            await asyncio.sleep(1)

async def run_monitoring_with_logical_tasks():
    """Run parallel monitoring with integrated telegram bot"""
    global bot_task
    import settings
    
    try:
        print("🔧 Importing settings...")
        print(f"📱 Found {len(settings.DEVICE_IDS)} devices: {settings.DEVICE_IDS}")
        
        await optimize_emulators()
        
        print("📊 Printing device states...")
        device_state_manager.print_all_device_states()
        
        # Start Telegram bot as background task
        bot_task = asyncio.create_task(start_telegram_bot())
        print("✅ Telegram bot started in background")
        
        # Create monitoring tasks for each device
        print("🚀 Creating monitoring tasks...")
        device_tasks = []
        for device_id in settings.DEVICE_IDS:
            print(f"📋 Creating task for {device_id}")
            task = asyncio.create_task(monitor_single_device_with_logical_tasks(device_id))
            device_tasks.append(task)
        
        print(f"✅ Created {len(device_tasks)} monitoring tasks")
        print("🔄 Starting parallel monitoring...")
        
        # Run all tasks together (bot + device monitoring)
        all_tasks = device_tasks + [bot_task]
        await asyncio.gather(*all_tasks)
        
    except Exception as e:
        print(f"❌ Error in run_monitoring_with_logical_tasks: {e}")
        traceback.print_exc()
        if 'device_tasks' in locals():
            for task in device_tasks:
                if not task.done():
                    task.cancel()
        if bot_task and not bot_task.done():
            bot_task.cancel()
        raise

def main():
    """Main entry point"""
    atexit.register(cleanup_handler)
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    
    print("🚀 Starting background monitoring with Telegram bot...")
    print("📊 Loading device states...")
    
    try:
        print("🔄 Starting async monitoring loop...")
        asyncio.run(run_monitoring_with_logical_tasks())
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user.")
        cleanup_handler()
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        traceback.print_exc()
        cleanup_handler()
    finally:
        cleanup_handler()

if __name__ == '__main__':
    main()