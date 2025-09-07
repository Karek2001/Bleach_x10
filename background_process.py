# background_process.py - Enhanced Version with Smart Multi-Detection
import asyncio
import time
from typing import Optional, Dict, List, Set
from datetime import datetime
from collections import defaultdict

import settings
from actions import batch_check_pixels_enhanced, execute_tap, screenshot_manager, run_adb_command, task_tracker
from tasks import (
    Main_Tasks, 
    Restarting_Tasks, 
    Shared_Tasks, 
    Switcher_Tasks,
    GUILD_TUTORIAL_TASKS,
    Guild_Rejoin,
    Sell_Characters,
    HardStory_Tasks,
    SideStory
)

# Bleach game package name
BLEACH_PACKAGE_NAME = "com.klab.bleach"
BLEACH_ACTIVITY_NAME = "com.klab.bleach.MainActivity"


class ProcessMonitor:
    """Monitors game processes and manages task switching"""
    
    def __init__(self):
        self.device_process_states = {}
        self.check_interval = 10
        self.last_check_times = {}
        self.active_task_set = {}
        self.initial_setup_complete = {}  # Tracks if initial setup is done for a device
        self.last_action_time = {}
        self.action_count = {}
        self.last_action_name = {}
        
    async def is_bleach_running(self, device_id: str) -> bool:
        """Check if Bleach Brave Souls process is running on the device"""
        try:
            command = f"shell pidof {BLEACH_PACKAGE_NAME}"
            result = await run_adb_command(command, device_id)
            return bool(result.strip())
        except Exception as e:
            print(f"[{device_id}] Error checking Bleach process: {e}")
            return False
    
    async def launch_bleach(self, device_id: str):
        """Launch Bleach Brave Souls game"""
        try:
            print(f"[{device_id}] Launching Bleach Brave Souls...")
            command = f"shell monkey -p {BLEACH_PACKAGE_NAME} -c android.intent.category.LAUNCHER 1"
            await run_adb_command(command, device_id)
            await asyncio.sleep(3)
            print(f"[{device_id}] Game launch command sent")
        except Exception as e:
            print(f"[{device_id}] Error launching game: {e}")
    
    async def kill_and_restart_game(self, device_id: str):
        """Kill and restart the game"""
        try:
            print(f"[{device_id}] Killing game process...")
            await run_adb_command(f"shell am force-stop {BLEACH_PACKAGE_NAME}", device_id)
            await asyncio.sleep(2)
            await self.launch_bleach(device_id)
            self.set_active_tasks(device_id, "restarting")
            self.reset_action_tracking(device_id)
        except Exception as e:
            print(f"[{device_id}] Error restarting game: {e}")
    
    def reset_action_tracking(self, device_id: str):
        """Reset action tracking for a device"""
        self.last_action_time[device_id] = time.time()
        self.action_count[device_id] = {}
        self.last_action_name[device_id] = None
    
    def track_action(self, device_id: str, action_name: str) -> bool:
        """Track action and check for repetition. Returns True if should restart"""
        current_time = time.time()
        
        if device_id not in self.last_action_time:
            self.last_action_time[device_id] = current_time
            self.action_count[device_id] = {}
            self.last_action_name[device_id] = None
        
        # Check for 240 second inactivity
        if current_time - self.last_action_time[device_id] > 240:
            print(f"[{device_id}] No actions for 240 seconds - triggering restart")
            return True
        
        self.last_action_time[device_id] = current_time
        
        # Track repetition with lower threshold for template tasks
        if action_name not in self.action_count[device_id]:
            self.action_count[device_id][action_name] = 0
        
        if self.last_action_name[device_id] == action_name:
            self.action_count[device_id][action_name] += 1
            
            # Lower repetition threshold for certain tasks
            max_repetitions = 5 if "template" in action_name.lower() else 10
            
            if self.action_count[device_id][action_name] >= max_repetitions:
                print(f"[{device_id}] Action '{action_name}' repeated {max_repetitions} times - triggering restart")
                return True
        else:
            self.action_count[device_id][action_name] = 1
            self.last_action_name[device_id] = action_name
        
        return False
    
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
        """Get the currently active task set with shared and switcher tasks"""
        task_set = self.active_task_set.get(device_id, "restarting")
        
        task_map = {
            "main": Main_Tasks,
            "restarting": Restarting_Tasks,
            "guild_tutorial": GUILD_TUTORIAL_TASKS,
            "guild_rejoin": Guild_Rejoin,
            "sell_characters": Sell_Characters,
            "hardstory": HardStory_Tasks,
            "sidestory": SideStory
        }
        
        base_tasks = task_map.get(task_set, Restarting_Tasks)
        
        # Combine base tasks with shared tasks and switcher tasks
        all_tasks = base_tasks + Shared_Tasks + Switcher_Tasks
        
        # Sort by priority (lower number = higher priority)
        return sorted(all_tasks, key=lambda x: x.get('priority', 999))
    
    def set_active_tasks(self, device_id: str, task_set: str):
        """Set the active task set for a device"""
        valid_sets = ["main", "restarting", "guild_tutorial", "guild_rejoin", "sell_characters", "hardstory", "sidestory"]
        if task_set in valid_sets:
            self.active_task_set[device_id] = task_set
            
            task_names = {
                "main": "Main_Tasks",
                "restarting": "Restarting_Tasks",
                "guild_tutorial": "GUILD_TUTORIAL_TASKS",
                "guild_rejoin": "Guild_Rejoin",
                "sell_characters": "Sell_Characters",
                "hardstory": "HardStory_Tasks",
                "sidestory": "SideStory"
            }
            print(f"[{device_id}] Switched to {task_names.get(task_set, task_set)}")
    
    def is_initial_setup_needed(self, device_id: str) -> bool:
        """Checks if the initial setup logic needs to run for a device."""
        return not self.initial_setup_complete.get(device_id, False)
    
    def mark_initial_complete(self, device_id: str):
        """Marks that the initial setup for a device is complete."""
        self.initial_setup_complete[device_id] = True


class OptimizedBackgroundMonitor:
    def __init__(self):
        self.stop_event = asyncio.Event()
        self.check_interval = getattr(settings, 'BACKGROUND_CHECK_INTERVAL', 0.2)
        self.batch_size = getattr(settings, 'TASK_BATCH_SIZE', 20)  # Increased for shared detection
        self.device_states = {}
        self.parallel_screenshots = getattr(settings, 'PARALLEL_SCREENSHOT_CAPTURE', True)
        self.max_concurrent_screenshots = getattr(settings, 'MAX_CONCURRENT_SCREENSHOTS', 16)
        self.process_monitor = ProcessMonitor()
        self.no_action_timers = {}
        self.frame_processed_tasks: Dict[str, Set[str]] = defaultdict(set)  # Track tasks processed per frame
        self.device_sleep_until: Dict[str, float] = {}  # Track when each device's sleep ends
    
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
    
    async def execute_tap_with_offset(self, device_id: str, location_str: str, task: dict):
        """Execute tap with optional pixel offset adjustments"""
        # Skip execution if coordinates are "0,0" (detection-only tasks)
        if location_str == "0,0":
            print(f"[{device_id}] Skipping click execution for coordinates '0,0' - detection-only task")
            return
            
        coords = location_str.split(',')
        x, y = int(coords[0]), int(coords[1])
        
        # Apply offset adjustments if specified
        if 'UpPixels' in task:
            y -= task['UpPixels']
        if 'DownPixels' in task:
            y += task['DownPixels']
        if 'LeftPixels' in task:
            x -= task['LeftPixels']
        if 'RightPixels' in task:
            x += task['RightPixels']
        
        # Execute tap at adjusted position
        adjusted_location = f"{x},{y}"
        await execute_tap(device_id, adjusted_location)

    def get_prioritized_tasks(self, device_id: str) -> List[dict]:
        """Return tasks already sorted by priority from get_active_tasks"""
        return self.process_monitor.get_active_tasks(device_id)

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
    
    async def handle_task_flags(self, device_id: str, task: dict):
        """Handle all task switching flags"""
        flag_handlers = {
            "BackToStory": ("main", "BackToStory triggered - switching to Main_Tasks"),
            "NeedGuildTutorial": ("guild_tutorial", "Guild tutorial detected - switching to GUILD_TUTORIAL_TASKS"),
            "NeedToRejoin": ("guild_rejoin", "Need to rejoin guild - switching to Guild_Rejoin"),
            "isRefreshed": ("guild_tutorial", "Guild refresh complete - returning to GUILD_TUTORIAL_TASKS"),
            "BackToRestartingTasks": ("restarting", "BackToRestartingTasks triggered - returning to Restarting_Tasks"),
            "BackToMain": ("main", "BackToMain triggered - returning to Main_Tasks"),
            "Characters_Full": ("sell_characters", "Characters_Full triggered - switching to Sell_Characters"),
            "HardStory": ("hardstory", "HardStory triggered - switching to HardStory_Tasks"),
            "SideStory": ("sidestory", "SideStory triggered - switching to SideStory")
        }
        
        for flag, (task_set, message) in flag_handlers.items():
            if task.get(flag, False):
                shows_in = task.get("ShowsIn")
                if shows_in:
                    current_task_set = self.process_monitor.active_task_set.get(device_id, "restarting")
                    task_set_mapping = {
                        "main": "main_tasks",
                        "restarting": "restarting_tasks", 
                        "guild_tutorial": "guild_tutorial_tasks",
                        "guild_rejoin": "guild_rejoin_tasks",
                        "sell_characters": "sell_characters_tasks",
                        "hardstory": "hardstory_tasks",
                        "sidestory": "sidestory_tasks"
                    }
                    current_task_name = task_set_mapping.get(current_task_set, current_task_set)
                    
                    if current_task_name not in shows_in:
                        print(f"[{device_id}] Flag '{flag}' ignored - not active in current task set '{current_task_name}'")
                        continue
                
                print(f"[{device_id}] {message}")
                self.process_monitor.set_active_tasks(device_id, task_set)
                break

    async def process_matched_tasks(self, device_id: str, matched_tasks: List[dict]) -> bool:
        """Process all matched tasks intelligently"""
        logical_triggered = False
        tasks_by_priority = defaultdict(list)
        
        # Group tasks by priority
        for task in matched_tasks:
            priority = task.get('priority', 999)
            tasks_by_priority[priority].append(task)
        
        # Process tasks by priority level
        for priority in sorted(tasks_by_priority.keys()):
            priority_tasks = tasks_by_priority[priority]
            
            # Within same priority, execute all shared_detection tasks
            shared_tasks = [t for t in priority_tasks if t.get('shared_detection', False)]
            regular_tasks = [t for t in priority_tasks if not t.get('shared_detection', False)]
            
            # Execute all shared detection tasks at this priority level
            for task in shared_tasks:
                task_name = task['task_name']
                
                # Skip if already processed in this frame
                if task_name in self.frame_processed_tasks[device_id]:
                    continue
                
                print(f"[{device_id}] {task_name} triggered (Priority: {priority}, Shared Detection)")
                
                self.no_action_timers[device_id] = time.time()
                self.frame_processed_tasks[device_id].add(task_name)
                
                # Check for restart conditions
                should_restart = self.process_monitor.track_action(device_id, task_name)
                if should_restart:
                    await self.process_monitor.kill_and_restart_game(device_id)
                    return logical_triggered
                
                # Handle task flags
                await self.handle_task_flags(device_id, task)
                
                # Execute the action if not already done
                if "[Multi:" not in task_name and "[Executed" not in task_name:
                    await self.execute_tap_with_offset(device_id, task["click_location_str"], task)
                
                # Handle sleep if specified
                if "sleep" in task:
                    sleep_duration = float(task["sleep"])
                    self.device_sleep_until[device_id] = time.time() + sleep_duration
                    print(f"[{device_id}] Sleeping for {sleep_duration} seconds after {task_name}")
                
                if task.get("isLogical", False):
                    logical_triggered = True
                    print(f"[{device_id}] DEBUG: Logical task detected - {task['task_name']}")
                    # Store task info for logical processing
                    if not hasattr(self, 'logical_task_info'):
                        self.logical_task_info = {}
                    self.logical_task_info[device_id] = task
                    print(f"[{device_id}] DEBUG: Stored logical task info with HardModeSwipe={task.get('HardModeSwipe', False)}")
                    print(f"[{device_id}] DEBUG: Returning immediately after logical task detection")
                    return logical_triggered
                
                await asyncio.sleep(0.05)
            
            # Execute first regular task at this priority level
            if regular_tasks and not logical_triggered:
                task = regular_tasks[0]
                task_name = task['task_name']
                
                if task_name not in self.frame_processed_tasks[device_id]:
                    print(f"[{device_id}] {task_name} triggered (Priority: {priority})")
                    
                    self.no_action_timers[device_id] = time.time()
                    self.frame_processed_tasks[device_id].add(task_name)
                    
                    # Check for restart conditions
                    should_restart = self.process_monitor.track_action(device_id, task_name)
                    if should_restart:
                        await self.process_monitor.kill_and_restart_game(device_id)
                        return logical_triggered
                    
                    # Handle task flags
                    await self.handle_task_flags(device_id, task)
                    
                    # Execute the action
                    if "[Executed" not in task_name:
                        await self.execute_tap_with_offset(device_id, task["click_location_str"], task)
                    
                    if task.get("isLogical", False):
                        logical_triggered = True
                        print(f"[{device_id}] DEBUG: Logical task detected (regular) - {task['task_name']}")
                        # Store task info for logical processing
                        if not hasattr(self, 'logical_task_info'):
                            self.logical_task_info = {}
                        self.logical_task_info[device_id] = task
                        print(f"[{device_id}] DEBUG: Stored logical task info (regular) with HardModeSwipe={task.get('HardModeSwipe', False)}")
                    
                    # Break after first regular task to prevent spam
                        # Handle sleep if specified
                if "sleep" in task:
                    sleep_duration = float(task["sleep"])
                    self.device_sleep_until[device_id] = time.time() + sleep_duration
                    print(f"[{device_id}] Sleeping for {sleep_duration} seconds after {task_name}")
                
                if task.get("isLogical", False):
                    logical_triggered = True
                    print(f"[{device_id}] DEBUG: Logical task detected (regular) - {task['task_name']}")
                    if not hasattr(self, 'logical_task_info'):
                        self.logical_task_info = {}
                    self.logical_task_info[device_id] = task
                    print(f"[{device_id}] DEBUG: Stored logical task info (regular) with HardModeSwipe={task.get('HardModeSwipe', False)}")
                
                # Break after first regular task to prevent spam
                break
        
        return logical_triggered

    def is_device_sleeping(self, device_id: str) -> bool:
        """Check if device is currently in sleep mode"""
        if device_id not in self.device_sleep_until:
            return False
        
        current_time = time.time()
        if current_time < self.device_sleep_until[device_id]:
            return True
        else:
            # Sleep time has passed, clear it
            del self.device_sleep_until[device_id]
            return False
    async def watch_device_optimized(self, device_id: str) -> Optional[str]:
        """Optimized device watching with smart multi-detection"""
        print(f"[{device_id}] Starting optimized background monitoring with smart detection...")
        
        self.device_states[device_id] = {'stable_count': 0, 'last_action': time.time()}
        self.no_action_timers[device_id] = time.time()
        
        while not self.stop_event.is_set():
            try:
                # Check if device is sleeping
                if self.is_device_sleeping(device_id):
                    await asyncio.sleep(0.1)  # Short sleep to check again
                    continue
                
                # Clear frame processed tasks
                self.frame_processed_tasks[device_id].clear()
                
                # Check if 240 seconds passed without any action
                if time.time() - self.no_action_timers.get(device_id, time.time()) > 240:
                    print(f"[{device_id}] 240 seconds without actions - restarting game")
                    await self.process_monitor.kill_and_restart_game(device_id)
                    self.no_action_timers[device_id] = time.time()
                
                # Check process status
                if await self.process_monitor.should_check_process(device_id):
                    is_bleach_running = await self.process_monitor.is_bleach_running(device_id)
                    
                    if self.process_monitor.is_initial_setup_needed(device_id):
                        if not is_bleach_running:
                            print(f"[{device_id}] Initial setup: Game not running, launching...")
                            await self.process_monitor.launch_bleach(device_id)
                            self.process_monitor.set_active_tasks(device_id, "restarting")
                        else:
                            print(f"[{device_id}] Initial setup: Game already running, using Main_Tasks.")
                            self.process_monitor.set_active_tasks(device_id, "main")
                        
                        self.process_monitor.mark_initial_complete(device_id)
                    
                    elif not is_bleach_running:
                        # This runs only after initial setup is complete (e.g., game crash)
                        print(f"[{device_id}] Game not running, re-launching...")
                        await self.process_monitor.launch_bleach(device_id)
                        self.process_monitor.set_active_tasks(device_id, "restarting")
                
                # Get all active tasks
                all_tasks = self.get_prioritized_tasks(device_id)
                
                # Process all tasks at once with the enhanced batch check
                matched_tasks = await batch_check_pixels_enhanced(device_id, all_tasks)
                
                if matched_tasks:
                    logical_triggered = await self.process_matched_tasks(device_id, matched_tasks)
                    print(f"[{device_id}] DEBUG: logical_triggered = {logical_triggered}")
                    if logical_triggered:
                        print(f"[{device_id}] DEBUG: Returning device_id for logical processing")
                        return device_id
                    
                    self.device_states[device_id]['stable_count'] = 0
                else:
                    self.device_states[device_id]['stable_count'] += 1
                
                interval = self.get_adaptive_interval(device_id)
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"[{device_id}] Error in monitoring: {e}")
                await asyncio.sleep(1)
        
        return None
    
    async def monitor_all_devices(self) -> Optional[str]:
        """Monitor all devices concurrently"""
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
    
    async def monitor_all_devices_ultra_fast(self) -> Optional[str]:
        """Ultra-fast monitoring with shared detection support"""
        self.stop_event.clear()
        
        for device_id in settings.DEVICE_IDS:
            self.no_action_timers[device_id] = time.time()
        
        while not self.stop_event.is_set():
            try:
                # Clear frame processed tasks for all devices
                for device_id in settings.DEVICE_IDS:
                    self.frame_processed_tasks[device_id].clear()
                
                # Check for devices that need restart
                for device_id in settings.DEVICE_IDS:
                    if time.time() - self.no_action_timers.get(device_id, time.time()) > 240:
                        print(f"[{device_id}] 240 seconds without actions - restarting game")
                        await self.process_monitor.kill_and_restart_game(device_id)
                        self.no_action_timers[device_id] = time.time()
                
                # Process checking for all devices
                async def check_and_manage_device(device_id: str):
                    try:
                        if await self.process_monitor.should_check_process(device_id):
                            is_bleach_running = await self.process_monitor.is_bleach_running(device_id)
                            
                            if self.process_monitor.is_initial_setup_needed(device_id):
                                if not is_bleach_running:
                                    print(f"[{device_id}] Initial setup: Game not running, launching...")
                                    await self.process_monitor.launch_bleach(device_id)
                                    self.process_monitor.set_active_tasks(device_id, "restarting")
                                else:
                                    print(f"[{device_id}] Initial setup: Game already running, using Main_Tasks.")
                                    self.process_monitor.set_active_tasks(device_id, "main")
                                
                                self.process_monitor.mark_initial_complete(device_id)
                            
                            elif not is_bleach_running:
                                # This runs only after initial setup is complete (e.g., game crash)
                                print(f"[{device_id}] Game not running, re-launching...")
                                await self.process_monitor.launch_bleach(device_id)
                                self.process_monitor.set_active_tasks(device_id, "restarting")
                    except Exception as e:
                        print(f"[{device_id}] Error in process check: {e}")
                
                # Check all devices concurrently
                process_check_tasks = [
                    asyncio.create_task(check_and_manage_device(device_id))
                    for device_id in settings.DEVICE_IDS
                ]
                
                await asyncio.gather(*process_check_tasks, return_exceptions=True)
                
                # Filter out sleeping devices for screenshot capture
                active_devices = [
                    device_id for device_id in settings.DEVICE_IDS 
                    if not self.is_device_sleeping(device_id)
                ]
                
                # Capture screenshots only from active (non-sleeping) devices
                device_screenshots = await self.batch_screenshot_all_devices(active_devices)
                
                # Process all active devices
                for device_id, screenshot in device_screenshots.items():
                    if screenshot is not None:
                        all_tasks = self.get_prioritized_tasks(device_id)
                        matched_tasks = await batch_check_pixels_enhanced(device_id, all_tasks, screenshot)
                        
                        if matched_tasks:
                            logical_triggered = await self.process_matched_tasks(device_id, matched_tasks)
                            if logical_triggered:
                                self.stop_event.set()
                                return device_id
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Ultra-fast monitor error: {e}")
                await asyncio.sleep(0.5)
        
        return None


# Global monitor instance
monitor = OptimizedBackgroundMonitor()

# Backward compatible functions
async def continuous_pixel_watch() -> Optional[str]:
    """Backward compatible wrapper for the optimized monitor"""
    return await monitor.monitor_all_devices()

async def watch_device_for_trigger(device_id: str) -> Optional[str]:
    """Backward compatible single device watcher"""
    return await monitor.watch_device_optimized(device_id)

