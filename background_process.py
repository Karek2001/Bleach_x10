# background_process.py - Enhanced with JSON flag support
import asyncio
import time
from typing import Optional, Dict, List, Set
from datetime import datetime
from collections import defaultdict

# Suppress warnings before importing OpenCV-related modules
from suppress_warnings import suppress_libpng_warning, suppress_stdout_stderr
suppress_libpng_warning()

import settings
from actions import batch_check_pixels_enhanced, execute_tap, screenshot_manager, run_adb_command, task_tracker
from device_state_manager import device_state_manager
from tasks import (
    StoryMode_Tasks, 
    Restarting_Tasks, 
    Shared_Tasks, 
    Switcher_Tasks,
    GUILD_TUTORIAL_TASKS,
    Guild_Rejoin,
    Sell_Characters,
    Sell_Accessury,
    HardStory_Tasks,
    SideStory,
    SubStories,
    SubStories_check,
    Character_Slots_Purchase,
    Exchange_Gold_Characters,
    Recive_GiftBox,
    Recive_Giftbox_Check,
    Skip_Kon_Bonaza,
    Skip_Yukio_Event_Tasks,
    Sort_Characters_Lowest_Level_Tasks,
    Sort_Filter_Ascension_Tasks,
    Sort_Multi_Select_Garbage_First_Tasks,
    Upgrade_Characters_Level,
    Upgrade_Characters_Back_To_Edit
)

# Bleach game package name
BLEACH_PACKAGE_NAME = "com.klab.bleach"
BLEACH_ACTIVITY_NAME = "com.klab.bleach.MainActivity"


class ProcessMonitor:
    """Monitors game processes and manages task switching with state persistence"""
    
    def __init__(self):
        self.device_process_states = {}
        self.check_interval = 10
        self.last_check_times = {}
        self.active_task_set = {}
        self.initial_setup_complete = {}
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
            print(f"[{device_id}] Error checking process")
            return False
    
    async def launch_bleach(self, device_id: str):
        """Launch Bleach Brave Souls game"""
        try:
            print(f"[{device_id}] Launching game...")
            command = f"shell monkey -p {BLEACH_PACKAGE_NAME} -c android.intent.category.LAUNCHER 1"
            await run_adb_command(command, device_id)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"[{device_id}] Error launching game")
    
    async def kill_and_restart_game(self, device_id: str):
        """Kill and restart the game with force stop"""
        try:
            print(f"[{device_id}] Restarting game...")
            await run_adb_command(f"shell am force-stop {BLEACH_PACKAGE_NAME}", device_id)
            await asyncio.sleep(2)
            await self.launch_bleach(device_id)
            
            # Increment restarting count in device state
            device_state_manager.increment_counter(device_id, "RestartingCount")
            
            # Set to restarting tasks initially
            self.set_active_tasks(device_id, "restarting")
            self.reset_action_tracking(device_id)
        except Exception as e:
            print(f"[{device_id}] Error restarting game")
    
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
            print(f"[{device_id}] No actions for 240s - restart needed")
            return True
        
        self.last_action_time[device_id] = current_time
        
        # Track repetition
        if action_name not in self.action_count[device_id]:
            self.action_count[device_id][action_name] = 0
        
        if self.last_action_name[device_id] == action_name:
            self.action_count[device_id][action_name] += 1
            
            max_repetitions = 5 if "template" in action_name.lower() else 13
            
            if self.action_count[device_id][action_name] >= max_repetitions:
                print(f"[{device_id}] Task repeated {max_repetitions}x - restart needed")
                return True
        else:
            self.action_count[device_id][action_name] = 1
            self.last_action_name[device_id] = action_name
        
        # Update session stats
        device_state_manager.update_session_stats(device_id, action_name)
        
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
    
    def should_skip_task(self, device_id: str, task: dict) -> bool:
        """Check if a task should be skipped based on StopSupport flag or ConditionalRun"""
        
        # FIRST: Check StopSupport flag (should prevent task from running)
        stop_support = task.get("StopSupport")
        if stop_support:
            should_stop = device_state_manager.check_stop_support(device_id, stop_support)
            if should_stop:
                # Special debug logging for Yukio retry tasks
                if "Yukio" in task.get("task_name", "") and "Retry" in task.get("task_name", ""):
                    state = device_state_manager.get_state(device_id)
                    retry_count = state.get("Skip_Yukio_Event_Retry_Count", 0)
                    print(f"[{device_id}] BLOCKING Retry task - count already at {retry_count}/3")
                return True
        
        # SECOND: Check ConditionalRun - skip task if conditions are NOT met
        conditional_run = task.get("ConditionalRun")
        if conditional_run and isinstance(conditional_run, list):
            device_state = device_state_manager.get_state(device_id)
            
            for key in conditional_run:
                # Special handling for Skip_Yukio_Event_Retry_At_3
                if key == "Skip_Yukio_Event_Retry_At_3":
                    retry_count = device_state.get("Skip_Yukio_Event_Retry_Count", 0)
                    if retry_count < 3:
                        # Special debug for Home button task
                        if "Home" in task.get("task_name", ""):
                            print(f"[{device_id}] Home button blocked - retry count {retry_count}/3")
                        return True  # Skip task, condition not met
                else:
                    value = device_state.get(key, 0)
                    if value != 1:
                        return True  # Skip task if any condition is not met
        
        return False
    
    def get_active_tasks(self, device_id: str) -> List[dict]:
        """Get the currently active task set with shared and switcher tasks, filtered by StopSupport"""
        task_set = self.active_task_set.get(device_id, "restarting")
        
        task_map = {
            "main": StoryMode_Tasks,
            "restarting": Restarting_Tasks,
            "guild_tutorial": GUILD_TUTORIAL_TASKS,
            "guild_rejoin": Guild_Rejoin,
            "sell_characters": Sell_Characters,
            "sell_accsesurry": Sell_Accessury,
            "hardstory": HardStory_Tasks,
            "sidestory": SideStory,
            "substories": SubStories,
            "substories_check": SubStories_check,
            "character_slots_purchase": Character_Slots_Purchase,
            "exchange_gold_characters": Exchange_Gold_Characters,
            "recive_giftbox": Recive_GiftBox,
            "recive_giftbox_check": Recive_Giftbox_Check,
            "skip_kon_bonaza": Skip_Kon_Bonaza,
            "skip_yukio_event": Skip_Yukio_Event_Tasks,
            "sort_characters_lowest_level": Sort_Characters_Lowest_Level_Tasks,
            "sort_filter_ascension": Sort_Filter_Ascension_Tasks,
            "sort_multi_select_garbage_first": Sort_Multi_Select_Garbage_First_Tasks,
            "upgrade_characters_level": Upgrade_Characters_Level,
            "upgrade_characters_back_to_edit": Upgrade_Characters_Back_To_Edit
        }
        
        # Debug: Log which task set is active and how many tasks it contains
        base_tasks = task_map.get(task_set, Restarting_Tasks)
        print(f"[{device_id}] Active task set: {task_set}, Base tasks: {len(base_tasks)}")
        
        # Debug: If substories is active, log the task names
        if task_set == "substories":
            task_names = [task.get("task_name", "Unknown") for task in base_tasks]
            print(f"[{device_id}] SubStories tasks: {task_names}")
        
        # Combine base tasks with shared tasks and switcher tasks
        all_tasks = base_tasks + Shared_Tasks + Switcher_Tasks
        
        # Filter out tasks with StopSupport flag if condition is met
        filtered_tasks = []
        for task in all_tasks:
            if not self.should_skip_task(device_id, task):
                filtered_tasks.append(task)
        
        # Sort by priority (lower number = higher priority)
        return sorted(filtered_tasks, key=lambda x: x.get('priority', 999))
    
    def set_active_tasks(self, device_id: str, task_set: str):
        """Set the active task set for a device and update state"""
        valid_sets = [
            "main", "restarting", "guild_tutorial", "guild_rejoin", 
            "sell_characters", "sell_accsesurry", "hardstory", "sidestory", 
            "substories", "substories_check",
            "character_slots_purchase",
            "exchange_gold_characters",
            "recive_giftbox",
            "recive_giftbox_check",
            "skip_kon_bonaza",
            "skip_yukio_event",
            "sort_characters_lowest_level",
            "sort_filter_ascension", 
            "sort_multi_select_garbage_first",
            "upgrade_characters_level",
            "upgrade_characters_back_to_edit"
        ]
        if task_set in valid_sets:
            self.active_task_set[device_id] = task_set
            
            # Update current task set in device state
            device_state_manager.update_state(device_id, "CurrentTaskSet", task_set)
            
            task_names = {
                "main": "Main",
                "restarting": "Restarting",
                "guild_tutorial": "Guild Tutorial",
                "guild_rejoin": "Guild Rejoin",
                "sell_characters": "Sell Characters",
                "sell_accsesurry": "Sell Accessory",
                "hardstory": "Hard Story",
                "sidestory": "Side Story",
                "substories": "Sub Stories",
                "substories_check": "Sub Stories Check",
                "character_slots_purchase": "Character Slots Purchase",
                "exchange_gold_characters": "Exchange Gold Characters",
                "recive_giftbox": "Receive Gift Box",
                "skip_kon_bonaza": "Skip Kon Bonanza",
                "skip_yukio_event": "Skip Yukio Event",
                "upgrade_characters_level": "Upgrade Characters Level",
                "upgrade_characters_back_to_edit": "Upgrade Characters Back To Edit"
            }
            print(f"[{device_id}] → {task_names.get(task_set, task_set)}")
    
    def is_initial_setup_needed(self, device_id: str) -> bool:
        """Checks if the initial setup logic needs to run for a device."""
        return not self.initial_setup_complete.get(device_id, False)
    
    def mark_initial_complete(self, device_id: str):
        """Marks that the initial setup for a device is complete."""
        self.initial_setup_complete[device_id] = True
    
    def should_use_saved_mode(self, device_id: str, current_task_set: str) -> str:
        """Check if we should switch to a different mode based on saved state"""
        if current_task_set == "restarting":
            recommended_mode = device_state_manager.should_skip_to_mode(device_id)
            if recommended_mode != "main":
                print(f"[{device_id}] State: Jumping to {recommended_mode}")
                return recommended_mode
        
        return current_task_set


class OptimizedBackgroundMonitor:
    def __init__(self):
        self.stop_event = asyncio.Event()
        self.check_interval = getattr(settings, 'BACKGROUND_CHECK_INTERVAL', 0.2)
        self.batch_size = getattr(settings, 'TASK_BATCH_SIZE', 20)
        self.device_states = {}
        self.parallel_screenshots = getattr(settings, 'PARALLEL_SCREENSHOT_CAPTURE', True)
        self.max_concurrent_screenshots = getattr(settings, 'MAX_CONCURRENT_SCREENSHOTS', 16)
        self.process_monitor = ProcessMonitor()
        self.no_action_timers = {}
        self.frame_processed_tasks: Dict[str, Set[str]] = defaultdict(set)
        self.device_sleep_until: Dict[str, float] = {}
        self.keep_checking_until: Dict[str, float] = {}
        self.keep_checking_task: Dict[str, str] = {}
        
        # Print initial device states on startup
        device_state_manager.print_all_device_states()
        
    async def batch_screenshot_all_devices(self, device_list: List[str]) -> Dict[str, any]:
        """Capture screenshots from multiple devices in parallel"""
        semaphore = asyncio.Semaphore(self.max_concurrent_screenshots)
        
        async def capture_device_screenshot(device_id):
            async with semaphore:
                try:
                    with suppress_stdout_stderr():
                        return await screenshot_manager.get_screenshot(device_id)
                except Exception:
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
        """Execute tap with optional pixel offset adjustments and delayed click support"""
        if location_str == "0,0":
            return
            
        coords = location_str.split(',')
        x, y = int(coords[0]), int(coords[1])
        
        if 'UpPixels' in task:
            y -= task['UpPixels']
        if 'DownPixels' in task:
            y += task['DownPixels']
        if 'LeftPixels' in task:
            x -= task['LeftPixels']
        if 'RightPixels' in task:
            x += task['RightPixels']
        
        adjusted_location = f"{x},{y}"
        await execute_tap(device_id, adjusted_location)
        
        # Handle delayed click functionality
        delayed_click_location = task.get("delayed_click_location")
        delayed_click_delay = task.get("delayed_click_delay", 2.0)
        
        if delayed_click_location:
            print(f"[{device_id}] Executing delayed click at {delayed_click_location} after {delayed_click_delay}s")
            await asyncio.sleep(delayed_click_delay)
            await execute_tap(device_id, delayed_click_location)

    def get_prioritized_tasks(self, device_id: str) -> List[dict]:
        """Return tasks already sorted by priority from get_active_tasks, with KeepChecking filtering"""
        all_tasks = self.process_monitor.get_active_tasks(device_id)
        
        # Check if device is in KeepChecking mode
        current_time = time.time()
        if device_id in self.keep_checking_until:
            if current_time < self.keep_checking_until[device_id]:
                # Still in KeepChecking period - only return the specific task
                keep_checking_task_name = self.keep_checking_task.get(device_id)
                if keep_checking_task_name:
                    filtered_tasks = [task for task in all_tasks if task.get("task_name") == keep_checking_task_name]
                    if filtered_tasks:
                        return filtered_tasks
            else:
                # KeepChecking period expired - clear it
                del self.keep_checking_until[device_id]
                if device_id in self.keep_checking_task:
                    del self.keep_checking_task[device_id]
                print(f"[{device_id}] KeepChecking period expired, resuming normal task processing")
        
        return all_tasks

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
        """Handle all task switching flags and update device state"""
        
        # Handle dynamic conditional checking
        conditional_run = task.get("ConditionalRun")
        if conditional_run and isinstance(conditional_run, list):
            device_state = device_state_manager.get_state(device_id)
            
            # Check if all specified keys are set to 1
            all_conditions_met = True
            status_info = []
            
            for key in conditional_run:
                # Special handling for Stop/Support conditions
                if key == "Skip_Yukio_Event_Retry_At_3":
                    retry_count = device_state.get("Skip_Yukio_Event_Retry_Count", 0)
                    value = 1 if retry_count >= 3 else 0
                    status_info.append(f"{key}:{value}")
                    if value != 1:
                        all_conditions_met = False
                else:
                    value = device_state.get(key, 0)
                    status_info.append(f"{key}:{value}")
                    if value != 1:
                        all_conditions_met = False
            
            status_str = " ".join(status_info)
            
            if not all_conditions_met:
                print(f"[{device_id}] Conditions not met ({status_str}) → Skip task")
                return  # Skip this task, don't process its flags
            else:
                print(f"[{device_id}] All conditions met ({status_str}) → Process task flags")
        
        # Handle JSON flag updates first
        json_flags = [
            "json_EasyMode", "json_HardMode", "json_SideMode",
            "json_SubStory", "json_Character_Slots_Purchased",
            "json_Exchange_Gold_Characters", "json_Recive_GiftBox", "json_ScreenShot_MainMenu",
            "json_Skip_Yukio_Event", "json_Sort_Characters_Lowest_Level",
            "json_Sort_Filter_Ascension", "json_Sort_Multi_Select_Garbage_First",
            "json_Upgrade_Characters_Level"
        ]
        
        for flag in json_flags:
            if task.get(flag, False):
                device_state_manager.set_json_flag(device_id, flag, 1)
        
        # Handle Kon Bonanza increment
        if task.get("Increment_Kon_Bonaza", False):
            device_state_manager.increment_kon_bonaza_skip(device_id)
        
        # Handle Character Slots Count increment
        if task.get("Increment_Character_Slots_Count", False):
            device_state_manager.increment_character_slots_count(device_id)
        
        # IMPORTANT: For increment flags, we need to process them BEFORE task execution
        # to ensure proper blocking on the next check
        
        # Handle Yukio Event Retry Counter BEFORE other processing
        if task.get("Increment_Yukio_Retry", False):
            # Get current count before incrementing
            state = device_state_manager.get_state(device_id)
            current_count = state.get("Skip_Yukio_Event_Retry_Count", 0)
            
            # Increment the counter
            new_count = device_state_manager.increment_yukio_retry(device_id)
            print(f"[{device_id}] Yukio Retry: {current_count} → {new_count}/3")
            
            if new_count >= 3:
                print(f"[{device_id}] ✓ Yukio 3 retries complete - Next check will show Home button")
                # Force a state reload for all devices to ensure they see the updated count
                device_state_manager._save_state(device_id)
        
        # Handle reset BEFORE other flags
        if task.get("Reset_Yukio_Retry", False):
            device_state_manager.reset_yukio_retry(device_id)
            print(f"[{device_id}] Yukio Event Retry counter reset")
        
        # Handle ConditionalCheck for Kon Bonanza
        if task.get("type") == "ConditionalCheck":
            check_key = task.get("check_key")
            check_value = task.get("check_value")
            check_operator = task.get("check_operator", "==")
            
            state = device_state_manager.get_state(device_id)
            current_value = state.get(check_key, 0)
            
            condition_met = False
            if check_operator == ">=":
                condition_met = current_value >= check_value
            elif check_operator == "==":
                condition_met = current_value == check_value
            
            if condition_met and task.get("ScreenShot_MainMenu_Tasks"):
                print(f"[{device_id}] Kon Bonanza complete → Screenshot Main Menu")
                self.process_monitor.set_active_tasks(device_id, "screenshot_mainmenu")
                return
        
        # Legacy handling for backward compatibility
        if "Part 21 Finished Detected" in task.get("task_name", ""):
            device_state_manager.mark_easy_mode_complete(device_id)
            print(f"[{device_id}] ✓ EasyMode complete")
        
        if task.get("SideStory", False) and "Part 21 Hard Chapter END" in task.get("task_name", ""):
            device_state_manager.mark_hard_mode_complete(device_id)
            print(f"[{device_id}] ✓ HardMode complete")
        
        if "Part 24 Chapter END" in task.get("task_name", ""):
            device_state_manager.mark_side_mode_active(device_id)
            print(f"[{device_id}] ✓ SideMode complete")
        
        # Handle standard task switching flags (including new ones)
        flag_handlers = {
            "BackToStory": ("main", "→ Main"),
            "NeedGuildTutorial": ("guild_tutorial", "→ Guild Tutorial"),
            "NeedToRejoin": ("guild_rejoin", "→ Guild Rejoin"),
            "isRefreshed": ("guild_tutorial", "→ Guild Tutorial"),
            "BackToRestartingTasks": ("restarting", "→ Restarting"),
            "BackToMain": ("main", "→ Main"),
            "Characters_Full": ("sell_characters", "→ Sell Characters"),
            "SellAccsesurry": ("sell_accsesurry", "→ Sell Accessory"),
            "HardStory": ("hardstory", "→ Hard Story"),
            "SideStory": ("sidestory", "→ Side Story"),
            "Sub-Stores": ("substories", "→ Sub Stories"),
            "CheckSubStoriesAllCleared": ("substories_check", "→ Sub Stories Check"),
            "Character_Slots_Purchase_Tasks": ("character_slots_purchase", "→ Character Slots Purchase"),
            "Exchange_Gold_Characters_Tasks": ("exchange_gold_characters", "→ Exchange Gold Characters"),
            "Recive_GiftBox_Tasks": ("recive_giftbox", "→ Receive Gift Box"),
            "Recive_GiftBox_Check_Tasks": ("recive_giftbox_check", "→ Receive Gift Box Check"),
            "Skip_Kon_Bonaza_Tasks": ("skip_kon_bonaza", "→ Skip Kon Bonanza"),
            "Skip_Yukio_Event_Tasks": ("skip_yukio_event", "→ Skip Yukio Event"),
            "Sort_Characters_Lowest_Level_Tasks": ("sort_characters_lowest_level", "→ Sort Characters Lowest Level"),
            "Sort_Filter_Ascension_Tasks": ("sort_filter_ascension", "→ Sort Filter Ascension"),
            "Sort_Multi_Select_Garbage_First_Tasks": ("sort_multi_select_garbage_first", "→ Sort Multi Select Garbage First"),
            "Upgrade_Characters_Level_Tasks": ("upgrade_characters_level", "→ Upgrade Characters Level"),
            "Upgrade_Characters_Back_To_Edit_Tasks": ("upgrade_characters_back_to_edit", "→ Upgrade Characters Back To Edit"),
            "ScreenShot_MainMenu_Tasks": ("screenshot_mainmenu", "→ Screenshot Main Menu")
        }
        
        # Enhanced BackToStory handling with new progression logic
        if task.get("BackToStory", False):
            current_task_set = self.process_monitor.active_task_set.get(device_id, "restarting")
            if current_task_set == "restarting":
                # Use new progression logic from device_state_manager
                recommended_mode = device_state_manager.get_next_task_set_after_restarting(device_id)
                print(f"[{device_id}] Progression → {recommended_mode}")
                self.process_monitor.set_active_tasks(device_id, recommended_mode)
                return
        
        for flag, (task_set, message) in flag_handlers.items():
            if task.get(flag, False):
                if flag == "Upgrade_Characters_Back_To_Edit_Tasks":
                    print(f"[DEBUG] {device_id}: {flag} triggered, switching to {task_set}")
                
                shows_in = task.get("ShowsIn")
                if shows_in:
                    current_task_set = self.process_monitor.active_task_set.get(device_id, "restarting")
                    task_set_mapping = {
                        "main": "storymode_tasks",
                        "restarting": "restarting_tasks", 
                        "guild_tutorial": "guild_tutorial_tasks",
                        "guild_rejoin": "guild_rejoin_tasks",
                        "sell_characters": "sell_characters_tasks",
                        "hardstory": "hardstory_tasks",
                        "sidestory": "sidestory_tasks",
                        "substories": "substories_tasks",
                        "substories_check": "substories_check_tasks",
                        "recive_giftbox": "recive_giftbox",
                        "recive_giftbox_check": "recive_giftbox_check"
                    }
                    current_task_name = task_set_mapping.get(current_task_set, current_task_set)
                    
                    if current_task_name not in shows_in:
                        continue
                
                print(f"[{device_id}] {message}")
                self.process_monitor.set_active_tasks(device_id, task_set)
                break

    async def process_matched_tasks(self, device_id: str, matched_tasks: List[dict]) -> bool:
        """Process all matched tasks intelligently"""
        logical_triggered = False
        tasks_by_priority = defaultdict(list)
        
        for task in matched_tasks:
            priority = task.get('priority', 999)
            tasks_by_priority[priority].append(task)
        
        for priority in sorted(tasks_by_priority.keys()):
            priority_tasks = tasks_by_priority[priority]
            
            shared_tasks = [t for t in priority_tasks if t.get('shared_detection', False)]
            regular_tasks = [t for t in priority_tasks if not t.get('shared_detection', False)]
            
            for task in shared_tasks:
                task_name = task['task_name']
                
                if task_name in self.frame_processed_tasks[device_id]:
                    continue
                
                # IMPORTANT: Check if task should still be skipped BEFORE execution
                if self.process_monitor.should_skip_task(device_id, task):
                    print(f"[{device_id}] Task blocked by flags: {task_name}")
                    continue
                
                print(f"[{device_id}] {task_name}")
                
                self.no_action_timers[device_id] = time.time()
                self.frame_processed_tasks[device_id].add(task_name)
                
                # Process increment flags BEFORE click execution
                if task.get("Increment_Yukio_Retry", False):
                    new_count = device_state_manager.increment_yukio_retry(device_id)
                    # If we just hit 3, don't execute the click
                    if new_count >= 3:
                        print(f"[{device_id}] Yukio retry limit reached - skipping click")
                        continue
                
                # Track action for restart detection
                should_restart = self.process_monitor.track_action(device_id, task_name)
                if should_restart:
                    await self.process_monitor.kill_and_restart_game(device_id)
                    return logical_triggered
                
                # Handle other task flags
                await self.handle_task_flags(device_id, task)
                
                # Execute the click if not a detection-only task
                if task.get("click_location_str") != "0,0" and "[Multi:" not in task_name and "[Executed" not in task_name:
                    await self.execute_tap_with_offset(device_id, task["click_location_str"], task)
                
                # Handle KeepChecking flag
                if "KeepChecking" in task:
                    keep_checking_duration = float(task["KeepChecking"])
                    self.keep_checking_until[device_id] = time.time() + keep_checking_duration
                    self.keep_checking_task[device_id] = task_name
                    print(f"[{device_id}] KeepChecking '{task_name}' for {keep_checking_duration}s")
                
                if "sleep" in task:
                    sleep_duration = float(task["sleep"])
                    self.device_sleep_until[device_id] = time.time() + sleep_duration
                    print(f"[{device_id}] Sleeping {sleep_duration}s")
                
                if task.get("isLogical", False):
                    logical_triggered = True
                    if not hasattr(self, 'logical_task_info'):
                        self.logical_task_info = {}
                    self.logical_task_info[device_id] = task
                    return logical_triggered
                
                await asyncio.sleep(0.05)
            
            if regular_tasks and not logical_triggered:
                task = regular_tasks[0]
                task_name = task['task_name']
                
                if task_name not in self.frame_processed_tasks[device_id]:
                    # IMPORTANT: Check if task should still be skipped BEFORE execution
                    if self.process_monitor.should_skip_task(device_id, task):
                        print(f"[{device_id}] Task blocked by flags: {task_name}")
                        continue
                    
                    print(f"[{device_id}] {task_name}")
                    
                    self.no_action_timers[device_id] = time.time()
                    self.frame_processed_tasks[device_id].add(task_name)
                    
                    # Process increment flags BEFORE click execution
                    if task.get("Increment_Yukio_Retry", False):
                        new_count = device_state_manager.increment_yukio_retry(device_id)
                        # If we just hit 3, don't execute the click
                        if new_count >= 3:
                            print(f"[{device_id}] Yukio retry limit reached - skipping click")
                            continue
                    
                    # Track action for restart detection
                    should_restart = self.process_monitor.track_action(device_id, task_name)
                    if should_restart:
                        await self.process_monitor.kill_and_restart_game(device_id)
                        return logical_triggered
                    
                    # Handle other task flags
                    await self.handle_task_flags(device_id, task)
                    
                    # Execute the click if not a detection-only task
                    if task.get("click_location_str") != "0,0" and "[Executed" not in task_name:
                        await self.execute_tap_with_offset(device_id, task["click_location_str"], task)
                    
                    # Handle KeepChecking flag
                    if "KeepChecking" in task:
                        keep_checking_duration = float(task["KeepChecking"])
                        self.keep_checking_until[device_id] = time.time() + keep_checking_duration
                        self.keep_checking_task[device_id] = task_name
                        print(f"[{device_id}] KeepChecking '{task_name}' for {keep_checking_duration}s")
                    
                    if "sleep" in task:
                        sleep_duration = float(task["sleep"])
                        self.device_sleep_until[device_id] = time.time() + sleep_duration
                        print(f"[{device_id}] Sleeping {sleep_duration}s")
                    
                    if task.get("isLogical", False):
                        logical_triggered = True
                        if not hasattr(self, 'logical_task_info'):
                            self.logical_task_info = {}
                        self.logical_task_info[device_id] = task
                    
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
            del self.device_sleep_until[device_id]
            return False
    
    async def watch_device_optimized(self, device_id: str) -> Optional[str]:
        """Optimized device watching with smart multi-detection and state tracking"""
        print(f"[{device_id}] Starting monitoring...")
        print(f"[{device_id}] {device_state_manager.get_progress_summary(device_id)}")
        
        self.device_states[device_id] = {'stable_count': 0, 'last_action': time.time()}
        self.no_action_timers[device_id] = time.time()
        
        while not self.stop_event.is_set():
            try:
                if self.is_device_sleeping(device_id):
                    await asyncio.sleep(0.1)
                    continue
                
                self.frame_processed_tasks[device_id].clear()
                
                if time.time() - self.no_action_timers.get(device_id, time.time()) > 240:
                    print(f"[{device_id}] 240s timeout - restarting")
                    await self.process_monitor.kill_and_restart_game(device_id)
                    self.no_action_timers[device_id] = time.time()
                
                if await self.process_monitor.should_check_process(device_id):
                    is_bleach_running = await self.process_monitor.is_bleach_running(device_id)
                    
                    if self.process_monitor.is_initial_setup_needed(device_id):
                        if not is_bleach_running:
                            print(f"[{device_id}] Game not running, launching...")
                            await self.process_monitor.launch_bleach(device_id)
                            self.process_monitor.set_active_tasks(device_id, "restarting")
                            device_state_manager.increment_counter(device_id, "RestartingCount")
                        else:
                            recommended_mode = device_state_manager.should_skip_to_mode(device_id)
                            self.process_monitor.set_active_tasks(device_id, recommended_mode)
                        
                        self.process_monitor.mark_initial_complete(device_id)
                    
                    elif not is_bleach_running:
                        print(f"[{device_id}] Game crashed, re-launching...")
                        await self.process_monitor.launch_bleach(device_id)
                        self.process_monitor.set_active_tasks(device_id, "restarting")
                        device_state_manager.increment_counter(device_id, "RestartingCount")
                
                # Check if current task set is completed and should progress
                # Skip progression logic for intentional helper task switches
                helper_task_sets = [
                    "restarting",
                    "upgrade_characters_back_to_edit",
                    "recive_giftbox_check", 
                    "sort_filter_ascension",
                    "sort_multi_select_garbage_first",
                    "skip_yukio_event"
                ]
                current_task_set = self.process_monitor.active_task_set.get(device_id, "restarting")
                if current_task_set not in helper_task_sets:
                    recommended_mode = device_state_manager.get_next_task_set_after_restarting(device_id)
                    if recommended_mode != current_task_set:
                        print(f"[{device_id}] Task set '{current_task_set}' complete → {recommended_mode}")
                        self.process_monitor.set_active_tasks(device_id, recommended_mode)
                        continue  # Skip to next iteration with new task set
                
                all_tasks = self.get_prioritized_tasks(device_id)
                
                with suppress_stdout_stderr():
                    matched_tasks = await batch_check_pixels_enhanced(device_id, all_tasks)
                
                if matched_tasks:
                    logical_triggered = await self.process_matched_tasks(device_id, matched_tasks)
                    if logical_triggered:
                        return device_id
                    
                    self.device_states[device_id]['stable_count'] = 0
                else:
                    self.device_states[device_id]['stable_count'] += 1
                
                interval = self.get_adaptive_interval(device_id)
                await asyncio.sleep(interval)
                
            except Exception as e:
                print(f"[{device_id}] Monitoring error: {e}")
                import traceback
                traceback.print_exc()
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
        """Ultra-fast monitoring with shared detection support and state tracking"""
        self.stop_event.clear()
        
        for device_id in settings.DEVICE_IDS:
            self.no_action_timers[device_id] = time.time()
        
        while not self.stop_event.is_set():
            try:
                for device_id in settings.DEVICE_IDS:
                    self.frame_processed_tasks[device_id].clear()
                
                for device_id in settings.DEVICE_IDS:
                    if time.time() - self.no_action_timers.get(device_id, time.time()) > 240:
                        print(f"[{device_id}] 240s timeout - restarting")
                        await self.process_monitor.kill_and_restart_game(device_id)
                        self.no_action_timers[device_id] = time.time()
                
                async def check_and_manage_device(device_id: str):
                    try:
                        if await self.process_monitor.should_check_process(device_id):
                            is_bleach_running = await self.process_monitor.is_bleach_running(device_id)
                            
                            if self.process_monitor.is_initial_setup_needed(device_id):
                                if not is_bleach_running:
                                    await self.process_monitor.launch_bleach(device_id)
                                    self.process_monitor.set_active_tasks(device_id, "restarting")
                                    device_state_manager.increment_counter(device_id, "RestartingCount")
                                else:
                                    recommended_mode = device_state_manager.should_skip_to_mode(device_id)
                                    self.process_monitor.set_active_tasks(device_id, recommended_mode)
                                
                                self.process_monitor.mark_initial_complete(device_id)
                            
                            elif not is_bleach_running:
                                await self.process_monitor.launch_bleach(device_id)
                                self.process_monitor.set_active_tasks(device_id, "restarting")
                                device_state_manager.increment_counter(device_id, "RestartingCount")
                    except Exception:
                        pass
                
                process_check_tasks = [
                    asyncio.create_task(check_and_manage_device(device_id))
                    for device_id in settings.DEVICE_IDS
                ]
                
                await asyncio.gather(*process_check_tasks, return_exceptions=True)
                
                active_devices = [
                    device_id for device_id in settings.DEVICE_IDS 
                    if not self.is_device_sleeping(device_id)
                ]
                
                with suppress_stdout_stderr():
                    device_screenshots = await self.batch_screenshot_all_devices(active_devices)
                
                for device_id, screenshot in device_screenshots.items():
                    if screenshot is not None:
                        all_tasks = self.get_prioritized_tasks(device_id)
                        
                        with suppress_stdout_stderr():
                            matched_tasks = await batch_check_pixels_enhanced(device_id, all_tasks, screenshot)
                        
                        if matched_tasks:
                            logical_triggered = await self.process_matched_tasks(device_id, matched_tasks)
                            if logical_triggered:
                                self.stop_event.set()
                                return device_id
                
                await asyncio.sleep(self.check_interval)
                
            except Exception:
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