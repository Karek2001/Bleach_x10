# background_process.py - Enhanced Version with Game Process Monitoring
import asyncio
import time
from typing import Optional, Dict, List
from datetime import datetime, timedelta

import settings
from actions import batch_check_pixels, execute_tap, screenshot_manager, run_adb_command


# Main background tasks configuration
BACKGROUND_TASKS = [
    {
        "task_name": "Open Story Map",
        "type": "template",
        "template_path": "templates/MapStep.png",
        "roi": [1, 132, 955, 291],
        "confidence": 0.70,
        "use_match_position": True,
        "isLogical": False,
        "BackToStore": False,  # Default flag
    },
    {
        "task_name": "Click [Prepare To Battle]",
        "type": "template",
        "template_path": "templates/Prepare.png",
        "roi": [507, 458, 313, 60],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "BackToStore": False,
    },
    {
        "task_name": "Click [Start Quest]",
        "type": "template",
        "template_path": "templates/StartQuest.png",
        "roi": [578, 470, 288, 49],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "BackToStore": False,
    },
    {
        "task_name": "Click [Skip]",
        "type": "template",
        "template_path": "templates/Skip.png",
        "roi": [830, 1, 129, 59],
        "confidence": 0.70,
        "use_match_position": True,
        "isLogical": False,
        "BackToStore": False,
    },
    {
        "task_name": "Click White Tap Button",
        "type": "pixel",
        "click_location_str": "665,507",
        "search_array": ["917,13","#0e2988","671,500","#4e4e67"],
        "isLogical": False,
        "BackToStore": False,
    },
    {
        "task_name": "Click New Record Word To Open Next Quest Menu",
        "type": "pixel",
        "click_location_str": "449,503",
        "search_array": ["833,35","#ff0000","819,54","#ffffff","834,74","#ff0000"],
        "isLogical": False,
        "BackToStore": False,
    },
    {
        "task_name": "Click [Next Quest]",
        "type": "template",
        "template_path": "templates/NextQuest.png",
        "roi": [684, 488, 154, 41],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "BackToStore": False,
    },
    {
        "task_name": "New Record Quest Obtained",
        "type": "pixel",
        "click_location_str": "478,281",
        "search_array": ["170,273","#fefefe","810,187","#ff0000","798,209","#ffffff"],
        "isLogical": False,
        "BackToStore": False,
    },
    {
        "task_name": "Click [Cancel] For Friend Request",
        "type": "template",
        "template_path": "templates/Cancel.png",
        "roi": [263, 389, 153, 42],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "BackToStore": False,
    },
]

# Secondary background tasks for when Bleach game is running
BACKGROUND_TASKS_2 = [
    {
        "task_name": "Click [Thank You] For Mod Menu",
        "type": "pixel",
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        "isLogical": False,
        "BackToStore": False,
    },
    {
        "task_name": "Click [Game Start]",
        "type": "pixel",
        "click_location_str": "477,452",
        "search_array": ["880,490","#515151","937,512","#e60012"],
        "isLogical": False,
        "BackToStore": False,
    },
    {
        "task_name": "Click [No] For Entering Existing Quest",
        "type": "template",
        "template_path": "templates/No.png",
        "roi": [252, 339, 174, 57],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "BackToStore": False,
    },
    {
        "task_name": "Skip Any New Events/Windows Opened By Clicking [OK]",
        "type": "template",
        "template_path": "templates/OK.png",
        "roi": [27, 229, 918, 272],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "BackToStore": False,
    },
        {
        "task_name": "Open [SOLO] Menu",
        "type": "template",
        "template_path": "templates/Solo.png",
        "roi": [814, 420, 142, 118],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "BackToStore": False,
    },
    {
        "task_name": "Open Story Window",
        "type": "pixel",
        "click_location_str": "531,193",
        "search_array": ["479,146","#ebebea","457,184","#ffffff","524,191","#ffffff"],
        "isLogical": False,
        "BackToStore": True,
    },
    # Add more Bleach-specific tasks as needed
]

# Bleach game package name
BLEACH_PACKAGE_NAME = "com.klab.bleach"
BLEACH_ACTIVITY_NAME = "com.klab.bleach.MainActivity"


class ProcessMonitor:
    """Monitors game processes and manages task switching"""
    
    def __init__(self):
        self.device_process_states = {}  # device_id -> process state
        self.check_interval = 10  # Check every 10 seconds
        self.last_check_times = {}  # device_id -> last check timestamp
        self.active_task_set = {}  # device_id -> "main" or "bleach"
        
    async def is_bleach_running(self, device_id: str) -> bool:
        """Check if Bleach Brave Souls is running AND focused on the device"""
        try:
            # Check if the Bleach process is running
            command = f"shell pidof {BLEACH_PACKAGE_NAME}"
            result = await run_adb_command(command, device_id)
            
            # If no process, definitely not running
            if not result.strip():
                return False
            
            # Process exists, now check if it's in foreground
            return await self.is_bleach_in_foreground(device_id)
            
        except Exception as e:
            print(f"[{device_id}] Error checking Bleach process: {e}")
            return False
    
    async def is_bleach_in_foreground(self, device_id: str) -> bool:
        """Check if Bleach game is currently in the foreground/focused"""
        try:
            # Get current foreground activity
            command = "shell dumpsys activity activities | grep mCurrentFocus"
            result = await run_adb_command(command, device_id)
            
            # Check if Bleach package is in the current focus
            if BLEACH_PACKAGE_NAME in result:
                return True
            
            # Alternative method - check top activity
            command = "shell dumpsys activity recents | grep 'Recent #0'"
            result = await run_adb_command(command, device_id)
            
            if BLEACH_PACKAGE_NAME in result:
                return True
                
            print(f"[{device_id}] Bleach process running but not focused")
            return False
            
        except Exception as e:
            print(f"[{device_id}] Error checking foreground activity: {e}")
            return False
    
    async def launch_bleach(self, device_id: str):
        """Launch Bleach Brave Souls game"""
        try:
            print(f"[{device_id}] Launching Bleach Brave Souls...")
            command = f"shell monkey -p {BLEACH_PACKAGE_NAME} -c android.intent.category.LAUNCHER 1"
            await run_adb_command(command, device_id)
            await asyncio.sleep(3)  # Give the game time to start
            print(f"[{device_id}] Bleach Brave Souls launched successfully")
            
        except Exception as e:
            print(f"[{device_id}] Error launching Bleach: {e}")
    
    async def should_check_process(self, device_id: str) -> bool:
        """Determine if it's time to check the process status"""
        current_time = time.time()
        
        if device_id not in self.last_check_times:
            self.last_check_times[device_id] = 0
        
        time_since_last_check = current_time - self.last_check_times[device_id]
        
        if time_since_last_check >= self.check_interval:
            self.last_check_times[device_id] = current_time
            return True
        
        return False
    
    def get_active_tasks(self, device_id: str) -> List[dict]:
        """Get the currently active task set for a device"""
        task_set = self.active_task_set.get(device_id, "main")
        
        if task_set == "bleach":
            return BACKGROUND_TASKS_2
        else:
            return BACKGROUND_TASKS
    
    def set_active_tasks(self, device_id: str, task_set: str):
        """Set the active task set for a device"""
        if task_set in ["main", "bleach"]:
            self.active_task_set[device_id] = task_set
            print(f"[{device_id}] Switched to {task_set} task set")


# Global process monitor instance
process_monitor = ProcessMonitor()


class FreezeDetector:
    """Detects and handles game freeze conditions with timing logic"""
    
    def __init__(self):
        self.device_freeze_states = {}
        self.freeze_duration = 20
        self.verification_duration = 5
        
    def get_freeze_state(self, device_id: str) -> dict:
        """Get or create freeze state for a device"""
        if device_id not in self.device_freeze_states:
            self.device_freeze_states[device_id] = {
                'freeze_detected': False,
                'detection_start': None,
                'verification_start': None,
                'consecutive_detections': 0,
                'last_check': None
            }
        return self.device_freeze_states[device_id]
    
    def reset_freeze_state(self, device_id: str):
        """Reset freeze detection state for a device"""
        self.device_freeze_states[device_id] = {
            'freeze_detected': False,
            'detection_start': None,
            'verification_start': None,
            'consecutive_detections': 0,
            'last_check': None
        }
    
    async def check_freeze_condition(self, device_id: str, freeze_task: dict) -> bool:
        """Check if freeze pixels are currently detected"""
        try:
            matched_tasks = await batch_check_pixels(device_id, [freeze_task])
            return len(matched_tasks) > 0
        except Exception as e:
            print(f"[{device_id}] Error checking freeze condition: {e}")
            return False
    
    async def handle_freeze_detection(self, device_id: str, freeze_task: dict) -> bool:
        """Handle freeze detection with timing logic"""
        state = self.get_freeze_state(device_id)
        current_time = datetime.now()
        
        is_frozen = await self.check_freeze_condition(device_id, freeze_task)
        
        if is_frozen:
            if not state['freeze_detected']:
                print(f"[{device_id}] Freeze detected, starting 20-second timer...")
                state['freeze_detected'] = True
                state['detection_start'] = current_time
                state['consecutive_detections'] = 1
                state['last_check'] = current_time
                return False
            else:
                time_elapsed = (current_time - state['detection_start']).total_seconds()
                state['consecutive_detections'] += 1
                state['last_check'] = current_time
                
                if time_elapsed >= self.freeze_duration:
                    if state['verification_start'] is None:
                        print(f"[{device_id}] 20 seconds elapsed, starting verification period...")
                        state['verification_start'] = current_time
                        return False
                    
                    verification_elapsed = (current_time - state['verification_start']).total_seconds()
                    
                    if verification_elapsed >= self.verification_duration:
                        print(f"[{device_id}] Freeze confirmed after {time_elapsed:.1f} seconds. Restarting game...")
                        self.reset_freeze_state(device_id)
                        return True
                    else:
                        print(f"[{device_id}] Verifying freeze... ({verification_elapsed:.1f}/{self.verification_duration}s)")
                        return False
                else:
                    print(f"[{device_id}] Freeze persisting... ({time_elapsed:.1f}/{self.freeze_duration}s)")
                    return False
        else:
            if state['freeze_detected']:
                time_elapsed = (current_time - state['detection_start']).total_seconds()
                
                if time_elapsed < self.freeze_duration:
                    print(f"[{device_id}] Freeze cleared after {time_elapsed:.1f} seconds. Resetting timer.")
                    self.reset_freeze_state(device_id)
                    return False
                elif state['verification_start'] is not None:
                    verification_elapsed = (current_time - state['verification_start']).total_seconds()
                    
                    if verification_elapsed < self.verification_duration:
                        print(f"[{device_id}] Freeze cleared during verification. Monitoring...")
                        return False
                    else:
                        print(f"[{device_id}] Freeze resolved after verification. Resetting.")
                        self.reset_freeze_state(device_id)
                        return False
            
            return False


# Global freeze detector instance
freeze_detector = FreezeDetector()


class OptimizedBackgroundMonitor:
    def __init__(self):
        self.stop_event = asyncio.Event()
        self.check_interval = getattr(settings, 'BACKGROUND_CHECK_INTERVAL', 0.2)
        self.batch_size = getattr(settings, 'TASK_BATCH_SIZE', 8)
        self.device_states = {}
        self.parallel_screenshots = getattr(settings, 'PARALLEL_SCREENSHOT_CAPTURE', True)
        self.max_concurrent_screenshots = getattr(settings, 'MAX_CONCURRENT_SCREENSHOTS', 16)
        self.freeze_detector = freeze_detector
        self.process_monitor = process_monitor  # Add process monitor
        
    async def batch_screenshot_all_devices(self, device_list: List[str]) -> Dict[str, any]:
        """Capture screenshots from multiple devices in parallel"""
        semaphore = asyncio.Semaphore(self.max_concurrent_screenshots)
        
        async def capture_device_screenshot(device_id):
            async with semaphore:
                try:
                    return await screenshot_manager.get_screenshot(device_id)
                except Exception as e:
                    print(f"[{device_id}] Screenshot error: {e}")
                    return None
        
        screenshot_tasks = [
            asyncio.create_task(capture_device_screenshot(device_id)) 
            for device_id in device_list
        ]
        
        screenshots = await asyncio.gather(*screenshot_tasks, return_exceptions=True)
        
        return {
            device_id: screenshot 
            for device_id, screenshot in zip(device_list, screenshots)
            if screenshot is not None and not isinstance(screenshot, Exception)
        }

    def get_prioritized_tasks(self, device_id: str) -> List[dict]:
        """Return tasks sorted by priority for the current active task set"""
        # Get the active task set for this device
        active_tasks = self.process_monitor.get_active_tasks(device_id)
        
        if not getattr(settings, 'USE_TASK_PRIORITIZATION', True):
            return active_tasks
        
        high_priority_keywords = ['tap', 'touch', 'energy', 'login', 'white', 'close', 'skip']
        medium_priority_keywords = ['king', 'tutorial', 'upgrade', 'training', 'prepare']
        
        def get_priority(task):
            name_lower = task['task_name'].lower()
            if any(keyword in name_lower for keyword in high_priority_keywords):
                return 0
            elif any(keyword in name_lower for keyword in medium_priority_keywords):
                return 1
            else:
                return 2
        
        return sorted(active_tasks, key=get_priority)

    def get_adaptive_interval(self, device_id: str) -> float:
        """Get adaptive check interval based on device stability"""
        if not getattr(settings, 'ADAPTIVE_CHECK_INTERVAL', True):
            return self.check_interval
            
        device_state = self.device_states.get(device_id, {'stable_count': 0, 'last_action': 0})
        
        if device_state['stable_count'] > 10:
            return self.check_interval * 2
        elif device_state['stable_count'] > 5:
            return self.check_interval * 1.5
        else:
            return self.check_interval

    async def watch_device_optimized(self, device_id: str) -> Optional[str]:
        """Optimized device watching with process monitoring and task switching"""
        print(f"[{device_id}] Starting optimized background monitoring with process checking...")
        
        self.device_states[device_id] = {'stable_count': 0, 'last_action': time.time()}
        
        while not self.stop_event.is_set():
            try:
                # Check if we should verify process status
                if await self.process_monitor.should_check_process(device_id):
                    is_bleach_running = await self.process_monitor.is_bleach_running(device_id)
                    
                    if not is_bleach_running:
                        # Bleach is not running, launch it and switch to BACKGROUND_TASKS_2
                        print(f"[{device_id}] Bleach process not detected, launching game...")
                        await self.process_monitor.launch_bleach(device_id)
                        self.process_monitor.set_active_tasks(device_id, "bleach")
                    else:
                        # Check if we're in bleach mode when we shouldn't be
                        current_mode = self.process_monitor.active_task_set.get(device_id, "main")
                        if current_mode == "bleach":
                            print(f"[{device_id}] Bleach is running, maintaining bleach task mode")
                
                # Get current active tasks for this device
                prioritized_tasks = self.get_prioritized_tasks(device_id)
                
                # Find freeze task and separate from others
                freeze_task = None
                other_tasks = []
                for task in prioritized_tasks:
                    if task.get('task_name', '').startswith("Game Freezed"):
                        freeze_task = task
                    else:
                        other_tasks.append(task)
                
                # Handle freeze detection if applicable
                if freeze_task:
                    needs_restart = await self.freeze_detector.handle_freeze_detection(device_id, freeze_task)
                    if needs_restart:
                        print(f"[{device_id}] Freeze detected - continuing monitoring...")
                        self.device_states[device_id] = {
                            'stable_count': 0,
                            'last_action': time.time()
                        }
                        continue
                
                # Process other tasks in batches
                for i in range(0, len(other_tasks), self.batch_size):
                    if self.stop_event.is_set():
                        break
                    
                    batch = other_tasks[i:i + self.batch_size]
                    matched_tasks = await batch_check_pixels(device_id, batch)
                    
                    action_taken = False
                    for task in matched_tasks:
                        print(f"[{device_id}] {task['task_name']} triggered")
                        
                        # Check for BackToStore flag
                        if task.get("BackToStore", False):
                            print(f"[{device_id}] BackToStore flag detected - switching to main tasks")
                            self.process_monitor.set_active_tasks(device_id, "main")
                        
                        # Execute tap action
                        await execute_tap(device_id, task["click_location_str"])
                        
                        self.device_states[device_id] = {
                            'stable_count': 0, 
                            'last_action': time.time()
                        }
                        action_taken = True
                        
                        if task.get("isLogical", False):
                            return device_id
                        
                        await asyncio.sleep(0.1)
                    
                    if not action_taken:
                        self.device_states[device_id]['stable_count'] += 1
                
                interval = self.get_adaptive_interval(device_id)
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"[{device_id}] Error in monitoring: {e}")
                await asyncio.sleep(1)
        
        return None
    
    async def monitor_all_devices_ultra_fast(self) -> Optional[str]:
        """Ultra-fast monitoring with process checking"""
        self.stop_event.clear()
        
        while not self.stop_event.is_set():
            try:
                # Process checking for all devices - NOW CONCURRENT
                async def check_and_launch_device(device_id: str):
                    """Check process status and launch game for a single device"""
                    try:
                        if await self.process_monitor.should_check_process(device_id):
                            is_bleach_running = await self.process_monitor.is_bleach_running(device_id)
                            
                            if not is_bleach_running:
                                print(f"[{device_id}] Bleach not running, launching and switching tasks...")
                                await self.process_monitor.launch_bleach(device_id)
                                self.process_monitor.set_active_tasks(device_id, "bleach")
                    except Exception as e:
                        print(f"[{device_id}] Error in process check: {e}")
                
                # Create concurrent tasks for process checking on all devices
                process_check_tasks = [
                    asyncio.create_task(check_and_launch_device(device_id))
                    for device_id in settings.DEVICE_IDS
                ]
                
                # Wait for all process checks to complete
                await asyncio.gather(*process_check_tasks, return_exceptions=True)
                
                # Capture screenshots from all devices
                if self.parallel_screenshots:
                    device_screenshots = await self.batch_screenshot_all_devices(settings.DEVICE_IDS)
                else:
                    device_screenshots = {}
                    for device_id in settings.DEVICE_IDS:
                        device_screenshots[device_id] = await screenshot_manager.get_screenshot(device_id)
                
                # Create concurrent tasks to check all devices
                check_tasks = []
                for device_id, screenshot in device_screenshots.items():
                    if screenshot is not None:
                        task = asyncio.create_task(
                            self.check_device_tasks_with_screenshot(device_id, screenshot)
                        )
                        check_tasks.append((device_id, task))
                
                # Wait for any device to trigger logical task
                if check_tasks:
                    for device_id, task in check_tasks:
                        try:
                            triggered = await asyncio.wait_for(task, timeout=0.1)
                            if triggered:
                                self.stop_event.set()
                                return device_id
                        except asyncio.TimeoutError:
                            continue
                        except Exception as e:
                            print(f"[{device_id}] Check error: {e}")
                            continue
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Ultra-fast monitor error: {e}")
                await asyncio.sleep(0.5)
        
        return None
    
    async def check_device_tasks_with_screenshot(self, device_id: str, screenshot) -> bool:
        """Check device tasks with BackToStore flag handling"""
        try:
            prioritized_tasks = self.get_prioritized_tasks(device_id)
            
            freeze_task = None
            other_tasks = []
            for task in prioritized_tasks:
                if task.get('task_name', '').startswith("Game Freezed"):
                    freeze_task = task
                else:
                    other_tasks.append(task)
            
            if freeze_task:
                needs_restart = await self.freeze_detector.handle_freeze_detection(device_id, freeze_task)
                if needs_restart:
                    print(f"[{device_id}] Freeze detected - continuing monitoring...")
                    return False
            
            for i in range(0, len(other_tasks), self.batch_size):
                batch = other_tasks[i:i + self.batch_size]
                matched_tasks = await batch_check_pixels(device_id, batch, screenshot)
                
                for task in matched_tasks:
                    print(f"[{device_id}] {task['task_name']} triggered")
                    
                    # Check BackToStore flag
                    if task.get("BackToStore", False):
                        print(f"[{device_id}] BackToStore detected - switching to main tasks")
                        self.process_monitor.set_active_tasks(device_id, "main")
                    
                    await execute_tap(device_id, task["click_location_str"])
                    
                    if task.get("isLogical", False):
                        return True
                    
                    await asyncio.sleep(0.05)
            
            return False
            
        except Exception as e:
            print(f"[{device_id}] Task check error: {e}")
            return False

    async def monitor_all_devices(self) -> Optional[str]:
        """Monitor all devices concurrently with process checking"""
        self.stop_event.clear()
        
        if self.parallel_screenshots:
            return await self.monitor_all_devices_ultra_fast()
        
        tasks = [
            asyncio.create_task(self.watch_device_optimized(device_id))
            for device_id in settings.DEVICE_IDS
        ]
        
        done, pending = await asyncio.wait(
            tasks, 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        self.stop_event.set()
        
        triggered_device = None
        for task in done:
            result = await task
            if result:
                triggered_device = result
                break
        
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        return triggered_device


# Global monitor instance
monitor = OptimizedBackgroundMonitor()

# Backward compatible function
async def continuous_pixel_watch() -> Optional[str]:
    """Backward compatible wrapper for the optimized monitor"""
    return await monitor.monitor_all_devices()

# Alternative high-performance version
async def watch_device_for_trigger(device_id: str) -> Optional[str]:
    """Backward compatible single device watcher"""
    return await monitor.watch_device_optimized(device_id)