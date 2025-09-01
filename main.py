# main.py
import asyncio
import atexit
import signal
from background_process import continuous_pixel_watch
from screenrecord_manager import cleanup_all_screenrecord

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
        # Start continuous monitoring loop
        asyncio.run(continuous_pixel_watch())
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user.")
        cleanup_handler()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        cleanup_handler()
    finally:
        cleanup_handler()

if __name__ == '__main__':
    main()