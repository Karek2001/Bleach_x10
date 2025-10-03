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
from actions import (
    batch_check_pixels_enhanced, 
    ScreenshotManager,
    execute_tap,
    execute_text_input,
    execute_swipe,
    run_adb_command,
    save_screenshot_with_username
)
from device_state_manager import device_state_manager
from airtable_helper import airtable_helper
from airtable_sync import sync_device_to_airtable
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
    Recive_Gold_From_Box_For_Characters_Purchase,
    Exchange_Gold_Characters,
    Recive_GiftBox,
    Recive_Giftbox_Check,
    Recive_Giftbox_Orbs,
    Recive_Giftbox_Orbs_Check,
    Skip_Kon_Bonaza,
    Kon_Bonaza_1Match_Tasks,
    Skip_Yukio_Event_Tasks,
    Sort_Characters_Lowest_Level_Tasks,
    Sort_Filter_Ascension_Tasks,
    Sort_Multi_Select_Garbage_First_Tasks,
    Upgrade_Characters_Level,
    Upgrade_Characters_Back_To_Edit,
    Main_Screenshot_Tasks,
    Extract_Orb_Counts_Tasks,
    Extract_Account_ID_Tasks,
    Login1_Prepare_For_Link_Tasks,
    Login2_Klab_Login_Tasks,
    Login3_Wait_For_2FA_Tasks,
    Login4_Confirm_Link_Tasks,
    Endgame_Tasks,
    # Reroll tasks
    reroll_earse_gamedata_tasks,
    reroll_earse_gamedatapart2_tasks,
    reroll_tutorial_firstmatch_tasks,
    reroll_tutorial_characterchoose_tasks,
    reroll_tutorial_characterchoosepart2_tasks,
    reroll_tutorial_secondmatch_tasks,
    reroll_replaceichigowithfivestar_tasks
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
        self.time_limited_search_start = {}  # Track when time-limited search started
        self.time_limited_search_flags = defaultdict(set)  # Track which flags triggered time-limited search
        
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
        
        # Clear time-limited search state from OptimizedBackgroundMonitor if it exists
        # This is needed when switching task sets or restarting
        # The OptimizedBackgroundMonitor tracks time-limited searches separately
    
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
        
        # Special handling for BackToStory tasks - don't count as repetition
        if "Game Opened Ready To Use" in action_name:
            # This is expected to run once per restart, don't count as repetition
            self.action_count[device_id] = {}  # Reset counts when game is ready
            self.last_action_name[device_id] = action_name
            return False
        
        if self.last_action_name[device_id] == action_name:
            self.action_count[device_id][action_name] += 1
            
            max_repetitions = 5 if "template" in action_name.lower() else 13
            
            if self.action_count[device_id][action_name] >= max_repetitions:
                print(f"[{device_id}] Task '{action_name}' repeated {max_repetitions}x - restart needed")
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
        """Check if a task should be skipped based on StopSupport, RequireSupport flag, ConditionalRun or TimeLimitedSearch"""
        
        # Check for time-limited search tasks
        time_limit_seconds = task.get("TimeLimitedSearch")
        if time_limit_seconds:
            # This task has time-limited search - check if it should be skipped
            trigger_flag = None
            for key, value in task.items():
                if key.startswith("RequireFlag_") and value:
                    trigger_flag = key.replace("RequireFlag_", "")
                    break
            
            if trigger_flag:
                device_state = device_state_manager.get_state(device_id)
                flag_value = device_state.get(trigger_flag, 0)
                
                # Check if the flag just got set (and we haven't started timing yet)
                if flag_value == 1 and trigger_flag not in self.time_limited_search_flags.get(device_id, set()):
                    # Start the timer for this flag
                    self.time_limited_search_start[device_id] = time.time()
                    self.time_limited_search_flags[device_id].add(trigger_flag)
                    print(f"[{device_id}] ⏱️ Starting {time_limit_seconds}s time-limited search for '{task.get('task_name', 'Unknown')}'")
                    return False  # Allow the task to run
                
                # Check if we're within the time limit
                if flag_value == 1 and trigger_flag in self.time_limited_search_flags.get(device_id, set()):
                    elapsed = time.time() - self.time_limited_search_start.get(device_id, time.time())
                    if elapsed <= time_limit_seconds:
                        # Still within time limit, allow search
                        return False
                    else:
                        # Time limit exceeded, skip this task
                        if task.get('task_name', 'Unknown') not in getattr(self, 'time_limit_logged', set()):
                            print(f"[{device_id}] ⏱️ Time limit ({time_limit_seconds}s) expired for '{task.get('task_name', 'Unknown')}' - skipping")
                            if not hasattr(self, 'time_limit_logged'):
                                self.time_limit_logged = set()
                            self.time_limit_logged.add(task.get('task_name', 'Unknown'))
                            # Set the flag that indicates we've checked but didn't find it
                            complete_flag = task.get("SetFlag_Remembered_Check_Complete")
                            if complete_flag:
                                device_state_manager.update_state(device_id, "Remembered_Check_Complete", 1)
                                print(f"[{device_id}] ✅ Flag set: Remembered_Check_Complete = 1 (timeout)")
                        return True
                
                # Flag not set yet, normal blocking
                if flag_value != 1:
                    print(f"[{device_id}] Task '{task.get('task_name', 'Unknown')}' blocked - waiting for {trigger_flag}")
                    return True
        
        # FIRST: Check RequireSupport flag (task needs something to be true)
        require_support = task.get("RequireSupport")
        if require_support:
            should_require = device_state_manager.check_stop_support(device_id, require_support)
            task_name = task.get("task_name", "Unknown")
            print(f"[{device_id}] RequireSupport check: {task_name} needs {require_support} = {should_require}, skip={'YES' if not should_require else 'NO'}")
            if not should_require:  # If requirement is NOT met, skip task
                return True
        
        # SECOND: Check StopSupport flag (should prevent task from running)
        stop_support = task.get("StopSupport")
        if stop_support:
            should_stop = device_state_manager.check_stop_support(device_id, stop_support)
            task_name = task.get("task_name", "Unknown")
            print(f"[{device_id}] StopSupport check: {task_name} blocked by {stop_support} = {should_stop}, skip={'YES' if should_stop else 'NO'}")
            if should_stop:
                return True
        
        # Check ConditionalRun flag (existing functionality)
        conditional_run = task.get("ConditionalRun")
        if conditional_run:
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
        
        # Check RequireFlag_ flags (new sequential execution system)
        device_state = device_state_manager.get_state(device_id)
        for key, value in task.items():
            if key.startswith("RequireFlag_") and value:
                flag_name = key.replace("RequireFlag_", "")
                flag_value = device_state.get(flag_name, 0)
                if flag_value != 1:
                    # Don't log for time-limited tasks (already handled above)
                    if not task.get("TimeLimitedSearch"):
                        print(f"[{device_id}] Task '{task.get('task_name', 'Unknown')}' blocked - waiting for {flag_name}")
                    return True  # Skip task until required flag is set
        
        return False
        
    def get_active_tasks(self, device_id: str) -> List[dict]:
        """Get the currently active task set"""
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
            "recive_gold_from_box_for_characters_purchase": Recive_Gold_From_Box_For_Characters_Purchase,
            "exchange_gold_characters": Exchange_Gold_Characters,
            "recive_giftbox": Recive_GiftBox,
            "recive_giftbox_check": Recive_Giftbox_Check,
            "recive_giftbox_orbs": Recive_Giftbox_Orbs,
            "recive_giftbox_orbs_check": Recive_Giftbox_Orbs_Check,
            "skip_kon_bonaza": Skip_Kon_Bonaza,
            "kon_bonaza_1match_tasks": Kon_Bonaza_1Match_Tasks,
            "skip_yukio_event": Skip_Yukio_Event_Tasks,
            "sort_characters_lowest_level": Sort_Characters_Lowest_Level_Tasks,
            "sort_filter_ascension": Sort_Filter_Ascension_Tasks,
            "sort_multi_select_garbage_first": Sort_Multi_Select_Garbage_First_Tasks,
            "upgrade_characters_level": Upgrade_Characters_Level,
            "upgrade_characters_back_to_edit": Upgrade_Characters_Back_To_Edit,
            # Reroll tasks
            "reroll_earse_gamedata": reroll_earse_gamedata_tasks,
            "reroll_earse_gamedatapart2": reroll_earse_gamedatapart2_tasks,
            "reroll_tutorial_firstmatch": reroll_tutorial_firstmatch_tasks,
            "reroll_tutorial_characterchoose": reroll_tutorial_characterchoose_tasks,
            "reroll_tutorial_characterchoosepart2": reroll_tutorial_characterchoosepart2_tasks,
            "reroll_tutorial_secondmatch": reroll_tutorial_secondmatch_tasks,
            "reroll_replaceichigowithfivestar": reroll_replaceichigowithfivestar_tasks,
            # Other tasks
            "main_screenshot": Main_Screenshot_Tasks,
            "extract_orb_counts": Extract_Orb_Counts_Tasks,
            "extract_account_id": Extract_Account_ID_Tasks,
            "login1_prepare_for_link": Login1_Prepare_For_Link_Tasks,
            "login2_klab_login": Login2_Klab_Login_Tasks,
            "login3_wait_for_2fa": Login3_Wait_For_2FA_Tasks,
            "login4_confirm_link": Login4_Confirm_Link_Tasks,
            "endgame": Endgame_Tasks
        }
        
        # Get base tasks or default to restarting
        base_tasks = task_map.get(task_set, Restarting_Tasks)
        print(f"[{device_id}] Active task set: {task_set}, Base tasks: {len(base_tasks)}")
        
        # Check if we're in reroll phase - DON'T add Restarting_Tasks if we are
        device_state = device_state_manager.get_state(device_id)
        is_reroll_phase = (
            task_set.startswith("reroll_") or 
            device_state.get("Reroll_Earse_GameData", 1) == 0 or
            device_state.get("Reroll_Earse_GameDataPart2", 1) == 0 or
            device_state.get("Reroll_Tutorial_FirstMatch", 1) == 0 or
            device_state.get("Reroll_Tutorial_CharacterChoose", 1) == 0 or
            device_state.get("Reroll_Tutorial_CharacterChoosePart2", 1) == 0 or
            device_state.get("Reroll_Tutorial_SecondMatch", 1) == 0 or
            device_state.get("Reroll_ReplaceIchigoWithFiveStar", 1) == 0
        )
        
        # ALWAYS include Shared_Tasks and Switcher_Tasks for all task sets
        # Restarting_Tasks should ONLY be used when task_set is "restarting"
        if is_reroll_phase:
            # In reroll mode: only base tasks + shared + switcher (NO restarting)
            all_tasks = base_tasks + Shared_Tasks + Switcher_Tasks
        elif task_set == "restarting":
            # Restarting task set: restarting tasks are already the base tasks
            all_tasks = base_tasks + Shared_Tasks + Switcher_Tasks
        else:
            # Other task sets: only base + shared + switcher (NO restarting tasks)
            all_tasks = base_tasks + Shared_Tasks + Switcher_Tasks
            
        print(f"[{device_id}] Total tasks loaded: {len(all_tasks)} (Base: {len(base_tasks)}, Shared: {len(Shared_Tasks)}, Switcher: {len(Switcher_Tasks)})")
            
        # Filter out tasks with StopSupport flag if condition is met
        filtered_tasks = []
        skipped_count = 0
        for task in all_tasks:
            skip_result = self.should_skip_task(device_id, task)
            if not skip_result:
                filtered_tasks.append(task)
            else:
                skipped_count += 1
                # Debug log which tasks are being skipped
                task_name = task.get('task_name', 'Unknown')
                print(f"[{device_id}] *** FILTERING OUT TASK: {task_name} ***")
                if task_set == "character_slots_purchase":
                    print(f"[{device_id}] BLOCKED CHARACTER SLOT TASK: {task_name}")
        
        if skipped_count > 0:
            print(f"[{device_id}] Filtered: {len(all_tasks)} -> {len(filtered_tasks)} tasks ({skipped_count} blocked)")
        
        # Sort by priority (lower number = higher priority)
        return sorted(filtered_tasks, key=lambda x: x.get('priority', 999))
    
    def set_active_tasks(self, device_id: str, task_set: str):
        """Set the active task set for a device and update state"""
        valid_sets = [
            "main", "restarting", "guild_tutorial", "guild_rejoin", 
            "sell_characters", "sell_accsesurry", "hardstory", "sidestory", 
            "substories", "substories_check", "character_slots_purchase",
            "recive_gold_from_box_for_characters_purchase",
            "exchange_gold_characters", "recive_giftbox", "recive_giftbox_check",
            "recive_giftbox_orbs", "recive_giftbox_orbs_check", "skip_kon_bonaza",
            "kon_bonaza_1match_tasks", "skip_yukio_event", "sort_characters_lowest_level",
            "sort_filter_ascension", "sort_multi_select_garbage_first",
            "upgrade_characters_level", "upgrade_characters_back_to_edit",
            "reroll_earse_gamedata", "reroll_earse_gamedatapart2", "reroll_tutorial_firstmatch", "reroll_tutorial_characterchoose",
            "reroll_tutorial_characterchoosepart2", "reroll_tutorial_secondmatch", "reroll_replaceichigowithfivestar",
            "main_screenshot", "extract_orb_counts", "extract_account_id",
            "login1_prepare_for_link", "login2_klab_login", "login3_wait_for_2fa",
            "login4_confirm_link"
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
                "recive_gold_from_box_for_characters_purchase": "Receive Gold From Box For Characters Purchase",
                "exchange_gold_characters": "Exchange Gold Characters",
                "recive_giftbox": "Receive Gift Box",
                "recive_giftbox_check": "Receive Gift Box Check",
                "recive_giftbox_orbs": "Receive Gift Box Orbs",
                "recive_giftbox_orbs_check": "Receive Gift Box Orbs Check",
                "skip_kon_bonaza": "Skip Kon Bonanza",
                "kon_bonaza_1match_tasks": "Kon Bonanza 1 Match",
                "skip_yukio_event": "Skip Yukio Event",
                "sort_characters_lowest_level": "Sort Characters Lowest Level",
                "sort_filter_ascension": "Sort Filter Ascension",
                "sort_multi_select_garbage_first": "Sort Multi Select Garbage First",
                "upgrade_characters_level": "Upgrade Characters Level",
                "upgrade_characters_back_to_edit": "Upgrade Characters Back To Edit",
                "reroll_earse_gamedata": "Reroll Erase Game Data",
                "reroll_earse_gamedatapart2": "Reroll Erase Game Data Part 2", 
                "reroll_tutorial_firstmatch": "Reroll Tutorial First Match",
                "reroll_tutorial_characterchoose": "Reroll Tutorial Character Choose",
                "reroll_tutorial_characterchoosepart2": "Reroll Tutorial Character Choose Part 2",
                "reroll_tutorial_secondmatch": "Reroll Tutorial Second Match",
                "reroll_replaceichigowithfivestar": "Reroll Replace Ichigo",
                "main_screenshot": "Main Screenshot",
                "extract_orb_counts": "Extract Orb Counts",
                "extract_account_id": "Extract Account ID", 
                "login1_prepare_for_link": "Prepare For Link",
                "login2_klab_login": "KLAB Login", 
                "login3_wait_for_2fa": "Wait For 2FA",
                "login4_confirm_link": "Confirm Link"
            }
            print(f"[{device_id}] → {task_names.get(task_set, task_set)}")
    
    def is_initial_setup_needed(self, device_id: str) -> bool:
        """Checks if the initial setup logic needs to run for a device."""
        return not self.initial_setup_complete.get(device_id, False)
    
    def mark_initial_complete(self, device_id: str):
        """Marks that the initial setup for a device is complete."""
        self.initial_setup_complete[device_id] = True


class BackgroundMonitor:
    """Enhanced Background process monitoring with intelligent task management"""
    
    def __init__(self):
        self.process_monitor = ProcessMonitor()
        self.last_execution_times = {}
        self.max_restart_attempts = 3
        self.is_running = False
        self.account_id_attempts = {}  # Store account ID extraction attempts per device
        self.orb_multi_attempts = {}  # Store multiple orb attempts for consensus
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
        
        # Special handling for BackToStory tasks - don't count as repetition
        if "Game Opened Ready To Use" in action_name:
            # This is expected to run once per restart, don't count as repetition
            self.action_count[device_id] = {}  # Reset counts when game is ready
            self.last_action_name[device_id] = action_name
            return False
        
        if self.last_action_name[device_id] == action_name:
            self.action_count[device_id][action_name] += 1
            
            max_repetitions = 5 if "template" in action_name.lower() else 13
            
            if self.action_count[device_id][action_name] >= max_repetitions:
                print(f"[{device_id}] Task '{action_name}' repeated {max_repetitions}x - restart needed")
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
        """Check if a task should be skipped based on StopSupport, RequireSupport flag or ConditionalRun"""
        
        # FIRST: Check RequireSupport flag (task needs something to be true)
        require_support = task.get("RequireSupport")
        if require_support:
            should_require = device_state_manager.check_stop_support(device_id, require_support)
            task_name = task.get("task_name", "Unknown")
            print(f"[{device_id}] RequireSupport check: {task_name} needs {require_support} = {should_require}, skip={'YES' if not should_require else 'NO'}")
            if not should_require:  # If requirement is NOT met, skip task
                return True
        
        # SECOND: Check StopSupport flag (should prevent task from running)
        stop_support = task.get("StopSupport")
        if stop_support:
            should_stop = device_state_manager.check_stop_support(device_id, stop_support)
            task_name = task.get("task_name", "Unknown")
            print(f"[{device_id}] StopSupport check: {task_name} blocked by {stop_support} = {should_stop}, skip={'YES' if should_stop else 'NO'}")
            if should_stop:
                # Special debug logging for Yukio retry tasks
                if "Yukio" in task.get("task_name", "") and "Retry" in task.get("task_name", ""):
                    state = device_state_manager.get_state(device_id)
                    retry_count = state.get("Skip_Yukio_Event_Retry_Count", 0)
                    print(f"[{device_id}] BLOCKING Retry task - count already at {retry_count}/3")
                return True
        
        # THIRD: Check ConditionalRun - skip task if conditions are NOT met
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
            "recive_gold_from_box_for_characters_purchase": Recive_Gold_From_Box_For_Characters_Purchase,
            "exchange_gold_characters": Exchange_Gold_Characters,
            "recive_giftbox": Recive_GiftBox,
            "recive_giftbox_check": Recive_Giftbox_Check,
            "recive_giftbox_orbs": Recive_Giftbox_Orbs,
            "recive_giftbox_orbs_check": Recive_Giftbox_Orbs_Check,
            "skip_kon_bonaza": Skip_Kon_Bonaza,
            "kon_bonaza_1match_tasks": Kon_Bonaza_1Match_Tasks,
            "skip_yukio_event": Skip_Yukio_Event_Tasks,
            "sort_characters_lowest_level": Sort_Characters_Lowest_Level_Tasks,
            "sort_filter_ascension": Sort_Filter_Ascension_Tasks,
            "sort_multi_select_garbage_first": Sort_Multi_Select_Garbage_First_Tasks,
            "upgrade_characters_level": Upgrade_Characters_Level,
            "upgrade_characters_back_to_edit": Upgrade_Characters_Back_To_Edit,
            # Reroll tasks
            "reroll_earse_gamedata": reroll_earse_gamedata_tasks,
            "reroll_earse_gamedatapart2": reroll_earse_gamedatapart2_tasks,
            "reroll_tutorial_firstmatch": reroll_tutorial_firstmatch_tasks,
            "reroll_tutorial_characterchoose": reroll_tutorial_characterchoose_tasks,
            "reroll_tutorial_characterchoosepart2": reroll_tutorial_characterchoosepart2_tasks,
            "reroll_tutorial_secondmatch": reroll_tutorial_secondmatch_tasks,
            "reroll_replaceichigowithfivestar": reroll_replaceichigowithfivestar_tasks,
            # Other tasks
            "main_screenshot": Main_Screenshot_Tasks,
            "extract_orb_counts": Extract_Orb_Counts_Tasks,
            "extract_account_id": Extract_Account_ID_Tasks,
            "login1_prepare_for_link": Login1_Prepare_For_Link_Tasks,
            "login2_klab_login": Login2_Klab_Login_Tasks,
            "login3_wait_for_2fa": Login3_Wait_For_2FA_Tasks,
            "login4_confirm_link": Login4_Confirm_Link_Tasks,
            "endgame": Endgame_Tasks
        }
        
        # Debug: Log which task set is active and how many tasks it contains
        base_tasks = task_map.get(task_set, Restarting_Tasks)
        print(f"[{device_id}] Active task set: {task_set}, Base tasks: {len(base_tasks)}")
        
        # Debug: If substories is active, log the task names
        if task_set == "substories":
            task_names = [task.get("task_name", "Unknown") for task in base_tasks]
            print(f"[{device_id}] SubStories tasks: {task_names}")
        
        # Debug: If character_slots_purchase is active, log the task names
        if task_set == "character_slots_purchase":
            task_names = [task.get("task_name", "Unknown") for task in base_tasks]
            print(f"[{device_id}] CharacterSlots tasks: {task_names}")
            print(f"[{device_id}] WARNING: Character_Slots_Purchase tasks should be blocked by StopSupport!")
        
        # Check if we're in a reroll phase
        device_state = device_state_manager.get_state(device_id)
        is_reroll_phase = (
            task_set.startswith("reroll_") or 
            device_state.get("Reroll_Earse_GameData", 1) == 0 or
            device_state.get("Reroll_Earse_GameDataPart2", 1) == 0 or
            device_state.get("Reroll_Tutorial_FirstMatch", 1) == 0 or
            device_state.get("Reroll_Tutorial_CharacterChoose", 1) == 0 or
            device_state.get("Reroll_Tutorial_CharacterChoosePart2", 1) == 0 or
            device_state.get("Reroll_Tutorial_SecondMatch", 1) == 0 or
            device_state.get("Reroll_ReplaceIchigoWithFiveStar", 1) == 0
        )
        
        # Combine tasks - Restarting_Tasks should only be included when task_set is "restarting"
        if is_reroll_phase:
            # In reroll phase: only base tasks + shared + switcher (NO restarting)
            all_tasks = base_tasks + Shared_Tasks + Switcher_Tasks
            print(f"[{device_id}] Reroll mode active - Restarting tasks disabled")
        elif task_set == "restarting":
            # Restarting task set: include restarting tasks as they ARE the base tasks
            all_tasks = base_tasks + Shared_Tasks + Switcher_Tasks
        else:
            # Other task sets: only base + shared + switcher (NO restarting tasks)
            all_tasks = base_tasks + Shared_Tasks + Switcher_Tasks
        
        # Filter out tasks with StopSupport flag if condition is met
        filtered_tasks = []
        skipped_count = 0
        for task in all_tasks:
            skip_result = self.should_skip_task(device_id, task)
            if not skip_result:
                filtered_tasks.append(task)
            else:
                skipped_count += 1
                # Debug log which tasks are being skipped
                task_name = task.get('task_name', 'Unknown')
                print(f"[{device_id}] *** FILTERING OUT TASK: {task_name} ***")
                if task_set == "character_slots_purchase":
                    print(f"[{device_id}] BLOCKED CHARACTER SLOT TASK: {task_name}")
        
        if skipped_count > 0:
            print(f"[{device_id}] Filtered: {len(all_tasks)} -> {len(filtered_tasks)} tasks ({skipped_count} blocked)")
        
        # Sort by priority (lower number = higher priority)
        return sorted(filtered_tasks, key=lambda x: x.get('priority', 999))
    
    def set_active_tasks(self, device_id: str, task_set: str):
        """Set the active task set for a device and update state"""
        valid_sets = [
            "main", "restarting", "guild_tutorial", "guild_rejoin", 
            "sell_characters", "sell_accsesurry", "hardstory", "sidestory", 
            "substories", "substories_check",
            "character_slots_purchase",
            "recive_gold_from_box_for_characters_purchase",
            "exchange_gold_characters",
            "recive_giftbox",
            "recive_giftbox_check",
            "recive_giftbox_orbs",
            "recive_giftbox_orbs_check",
            "skip_kon_bonaza",
            "kon_bonaza_1match_tasks",
            "skip_yukio_event",
            "sort_characters_lowest_level",
            "sort_filter_ascension", 
            "sort_multi_select_garbage_first",
            "upgrade_characters_level",
            "upgrade_characters_back_to_edit",
            # Reroll task sets
            "reroll_earse_gamedata",
            "reroll_tutorial_firstmatch",
            "reroll_tutorial_characterchoose",
            "reroll_tutorial_secondmatch",
            "reroll_replaceichigowithfivestar",
            # Other task sets
            "main_screenshot",
            "extract_orb_counts",
            "extract_account_id",
            "login1_prepare_for_link",
            "login2_klab_login", 
            "login3_wait_for_2fa",
            "login4_confirm_link",
            "endgame"
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
                "recive_gold_from_box_for_characters_purchase": "Receive Gold From Box For Characters Purchase",
                "exchange_gold_characters": "Exchange Gold Characters",
                "recive_giftbox": "Receive Gift Box",
                "recive_giftbox_orbs": "Receive Gift Box Orbs",
                "recive_giftbox_orbs_check": "Receive Gift Box Orbs Check",
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
        self.text_input_active: Dict[str, float] = {}  # Track when text input is happening
        
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
        """Execute tap with optional pixel offset adjustments, delayed click, hold, and drag support"""
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
        
        # Handle hold_delay - hold the tap for specified seconds
        if "hold_delay" in task:
            hold_duration = float(task["hold_delay"])
            print(f"[{device_id}] 📍 Holding at {adjusted_location} for {hold_duration}s")
            # Use swipe with same start and end position to simulate hold
            await execute_swipe(device_id, x, y, x, y, int(hold_duration * 1000))
        # Handle hold_move - drag from one position to another  
        elif "hold_move" in task:
            target_coords = task["hold_move"].split(',')
            target_x, target_y = int(target_coords[0]), int(target_coords[1])
            # Default drag duration of 1 second if not specified
            drag_duration = int(task.get("drag_duration", 1) * 1000)
            print(f"[{device_id}] 📍 Dragging from {adjusted_location} to {target_x},{target_y} over {drag_duration/1000}s")
            await execute_swipe(device_id, x, y, target_x, target_y, drag_duration)
        else:
            # Normal tap
            await execute_tap(device_id, adjusted_location)
        
        # Handle delayed click functionality
        delayed_click_location = task.get("delayed_click_location")
        delayed_click_delay = task.get("delayed_click_delay", 2.0)
        
        if delayed_click_location:
            print(f"[{device_id}] Executing delayed click at {delayed_click_location} after {delayed_click_delay}s")
            await asyncio.sleep(delayed_click_delay)
            await execute_tap(device_id, delayed_click_location)

    async def handle_text_input_flags(self, device_id: str, task: dict):
        """Handle Enter_Email, Enter_Password, Enter_UserName, and Get_2fa flags after clicking"""
        
        # Check for Get_2fa flag (new functionality)
        if task.get("Get_2fa", False):
            print(f"[{device_id}] 2FA code requested - waiting 60 seconds for email to arrive...")
            await asyncio.sleep(60.0)  # Wait 60 seconds for email to arrive
            
            # Get email from device state
            device_state = device_state_manager.get_state(device_id)
            email = device_state.get("Email", "")
            
            if not email:
                print(f"[{device_id}] ⚠️ Warning: No email found in device state for 2FA retrieval")
                return
            
            print(f"[{device_id}] Retrieving 2FA code for email: {email}")
            
            # Get 2FA code from Airtable
            twofa_code = await airtable_helper.get_2fa_code(email)
            
            if twofa_code:
                print(f"[{device_id}] Entering 2FA code: {twofa_code}")
                await execute_text_input(device_id, twofa_code)
                print(f"[{device_id}] ✅ 2FA code entered successfully")
            else:
                print(f"[{device_id}] ❌ Error: Could not retrieve 2FA code from Airtable")
        
        # Check for Enter_Email flag (existing functionality)
        if task.get("Enter_Email", False):
            # Lock text input to pause all other tasks
            self.text_input_active[device_id] = time.time() + 15.0  # 15 second lock
            print(f"[{device_id}] 🔒 Text input locked - pausing all other tasks for 15s")
            
            await asyncio.sleep(3.0)  # 3 second delay before typing email
            device_state = device_state_manager.get_state(device_id)
            email = device_state.get("Email", "")
            if email:
                print(f"[{device_id}] Entering email: {email}")
                await execute_text_input(device_id, email)
                # Additional delay after email entry
                await asyncio.sleep(1.0)
                print(f"[{device_id}] ✅ Email entered, waiting 1s...")
            else:
                print(f"[{device_id}] Warning: No email found in device state")
            
            # Release text input lock
            if device_id in self.text_input_active:
                del self.text_input_active[device_id]
            print(f"[{device_id}] 🔓 Text input unlocked - resuming task detection")
        
        # Check for Enter_Password flag (existing functionality)
        if task.get("Enter_Password", False):
            # Lock text input to pause all other tasks
            self.text_input_active[device_id] = time.time() + 15.0  # Same 15 second lock as email
            print(f"[{device_id}] 🔒 Text input locked - pausing all other tasks for 15s")
            
            await asyncio.sleep(3.0)  # Same 3 second delay as email
            device_state = device_state_manager.get_state(device_id)
            password = device_state.get("Password", "")
            if password:
                print(f"[{device_id}] Entering password: {password}")  # Show actual password (no hiding)
                await execute_text_input(device_id, password)
                # Additional delay after password entry (same as email)
                await asyncio.sleep(1.0)
                print(f"[{device_id}] ✅ Password entered, waiting 1s...")
            else:
                print(f"[{device_id}] Warning: No password found in device state")
            
            # Release text input lock
            if device_id in self.text_input_active:
                del self.text_input_active[device_id]
            print(f"[{device_id}] 🔓 Text input unlocked - resuming task detection")
        
        # Check for Enter_UserName flag (new functionality)
        if task.get("Enter_UserName", False):
            # Lock text input to pause all other tasks
            self.text_input_active[device_id] = time.time() + 15.0  # Same 15 second lock as email and password
            print(f"[{device_id}] 🔒 Text input locked - pausing all other tasks for 15s")
            
            await asyncio.sleep(3.0)  # Same 3 second delay as email and password
            device_state = device_state_manager.get_state(device_id)
            username = device_state.get("UserName", "")
            if username:
                print(f"[{device_id}] Entering username: {username}")
                await execute_text_input(device_id, username)
                # Additional delay after username entry (same as email and password)
                await asyncio.sleep(1.0)
                print(f"[{device_id}] ✅ Username entered, waiting 1s...")
            else:
                print(f"[{device_id}] Warning: No username found in device state")
            
            # Release text input lock
            if device_id in self.text_input_active:
                del self.text_input_active[device_id]
            print(f"[{device_id}] 🔓 Text input unlocked - resuming task detection")

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
            "json_Recive_Gold_From_Box_For_Characters_Purchase",
            "json_Exchange_Gold_Characters", "json_Recive_GiftBox", "json_ScreenShot_MainMenu",
            "json_Skip_Yukio_Event", "json_Sort_Characters_Lowest_Level",
            "json_Sort_Filter_Ascension", "json_Sort_Multi_Select_Garbage_First",
            "json_Upgrade_Characters_Level", "json_Recive_Giftbox_Orbs",
            "json_isLinked",  # Missing flag for account linking status
            # Reroll task flags
            "json_Reroll_Earse_GameData",
            "json_Reroll_Earse_GameDataPart2",  # Second part of game data erase
            "json_Reroll_Tutorial_FirstMatch", 
            "json_Reroll_Tutorial_CharacterChoose",
            "json_Reroll_Tutorial_CharacterChoosePart2",  # Second part of character choose
            "json_Reroll_Tutorial_SecondMatch",
            "json_Reroll_ReplaceIchigoWithFiveStar"
        ]
        
        for flag in json_flags:
            if task.get(flag, False):
                device_state_manager.set_json_flag(device_id, flag, 1)
        
        # Handle increment_stock flag
        if task.get("increment_stock", False):
            device_state_manager.increment_stock(device_id)
        
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
        
        # Handle pre-delay for OCR accuracy
        if task.get("pre_delay", 0) > 0:
            pre_delay = task.get("pre_delay", 0)
            print(f"[{device_id}] ⏳ Pre-delay: waiting {pre_delay}s for screen to stabilize...")
            await asyncio.sleep(pre_delay)
        
        # Handle multi-attempt orb storage
        if task.get("store_orb_attempt", False):
            ocr_result = None
            
            # Try to get OCR result from task object first
            if hasattr(task, 'ocr_result') and task.ocr_result and task.ocr_result.strip():
                ocr_result = task.ocr_result.strip()
                print(f"[{device_id}] 🔍 Got OCR from task.ocr_result: '{ocr_result}'")
            
            # Fallback: Extract OCR result from task name (Enhanced OCR: 'value')
            elif 'Enhanced OCR:' in task.get('task_name', ''):
                import re
                task_name = task.get('task_name', '')
                match = re.search(r"Enhanced OCR: '([^']+)'", task_name)
                if match:
                    ocr_result = match.group(1).strip()
                    print(f"[{device_id}] 🔍 Extracted OCR from task name: '{ocr_result}'")
            
            if ocr_result:
                attempt_num = task.get("orb_multi_attempt", 0)
                print(f"[{device_id}] 🔄 Storing orb attempt {attempt_num}: '{ocr_result}'")
                self.store_multi_orb_attempt(device_id, attempt_num, ocr_result)
                
                # Check if this is a next_task_only task - don't trigger task set completion
                if task.get("next_task_only", False):
                    print(f"[{device_id}] ⏭️ Next task only - continuing to next attempt...")
                    return  # Don't process other completion logic
            else:
                print(f"[{device_id}] ⚠️ No valid OCR result found for orb attempt")
                print(f"[{device_id}] 🔍 Task name: '{task.get('task_name', 'N/A')}'")
                # Even if no OCR result, respect next_task_only to prevent early completion
                if task.get("next_task_only", False):
                    print(f"[{device_id}] ⏭️ Next task only (no OCR) - continuing anyway...")
                    return
            # Continue processing
        
        # Handle final orb consensus and extraction
        if task.get("orb_final_consensus", False):
            print(f"[{device_id}] 🎯 Final consensus check triggered")
            
            # Extract OCR result using same logic as above
            ocr_result = None
            if hasattr(task, 'ocr_result') and task.ocr_result and task.ocr_result.strip():
                ocr_result = task.ocr_result.strip()
            elif 'Enhanced OCR:' in task.get('task_name', ''):
                import re
                task_name = task.get('task_name', '')
                match = re.search(r"Enhanced OCR: '([^']+)'", task_name)
                if match:
                    ocr_result = match.group(1).strip()
            
            if ocr_result:
                # Store the final attempt
                attempt_num = task.get("orb_multi_attempt", 0)
                print(f"[{device_id}] 🔄 Storing final orb attempt {attempt_num}: '{ocr_result}'")
                self.store_multi_orb_attempt(device_id, attempt_num, ocr_result)
                
                # Get best consensus value
                best_orb = self.get_best_orb_consensus(device_id)
                if best_orb:
                    device_state_manager.update_state(device_id, "Orbs", best_orb)
                    print(f"[{device_id}] ✅ Best orb consensus: '{best_orb}'")
                else:
                    print(f"[{device_id}] ❌ No reliable orb consensus found")
            else:
                print(f"[{device_id}] ⚠️ No OCR result for final consensus")
            # Continue processing
        
        # Handle direct orb extraction (fallback - only for non-consensus tasks)
        if task.get("extract_orb_value", False) and not task.get("orb_final_consensus", False):
            if hasattr(task, 'ocr_result') and task.ocr_result:
                try:
                    cleaned_orb = self.robust_number_ocr_cleanup(device_id, task.ocr_result)
                    device_state_manager.update_state(device_id, "Orbs", cleaned_orb)
                    print(f"[{device_id}] ✅ Direct orb extraction: '{task.ocr_result}' → '{cleaned_orb}'")
                except Exception as e:
                    print(f"[{device_id}] ❌ Direct orb extraction failed: {e}")
                    # Don't crash, just continue without updating
            # Continue processing - don't return early
        
        # Handle direct account ID extraction (simplified)
        if task.get("extract_account_id_value", False):
            if hasattr(task, 'ocr_result') and task.ocr_result:
                try:
                    cleaned_account_id = self.robust_account_id_cleanup(device_id, task.ocr_result)
                    device_state_manager.update_state(device_id, "AccountID", cleaned_account_id)
                    print(f"[{device_id}] ✅ Account ID extracted: '{task.ocr_result}' → '{cleaned_account_id}'")
                except Exception as e:
                    print(f"[{device_id}] ❌ Account ID extraction failed: {e}")
                    # Don't crash, just continue without updating
            # Continue processing
        
        # Handle temporary account ID storage for consensus
        if task.get("temp_account_id_storage", False):
            attempt_num = task.get("account_id_extraction_attempt", 0)
            if hasattr(task, 'ocr_result') and task.ocr_result:
                self.store_account_id_attempt(device_id, attempt_num, task.ocr_result)
            # Continue processing - don't return early
        
        # Handle account ID consensus check
        if task.get("account_id_consensus_check", False):
            attempt_num = task.get("account_id_extraction_attempt", 0)
            if hasattr(task, 'ocr_result') and task.ocr_result:
                self.store_account_id_attempt(device_id, attempt_num, task.ocr_result)
                consensus_value = self.check_account_id_consensus(device_id)
                if consensus_value:
                    device_state_manager.update_state(device_id, "AccountID", consensus_value)
                    print(f"[{device_id}] ✅ Account ID consensus reached: {consensus_value}")
                else:
                    print(f"[{device_id}] ❌ No Account ID consensus - extraction failed")
                    return  # Don't trigger next task set if consensus failed
            
        # Handle Airtable sync flag
        if task.get("sync_to_airtable", False):
            print(f"[{device_id}] Airtable sync requested")
            sync_device_to_airtable(device_id)
            return
        
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
                self.process_monitor.set_active_tasks(device_id, "main_screenshot")
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
            "NeedGuildTutorial": ("guild_tutorial", "→ Guild Tutorial"),
            "NeedToRejoin": ("guild_rejoin", "→ Guild Rejoin"),
            "isRefreshed": ("guild_tutorial", "→ Guild Tutorial"),
            "BackToRestartingTasks": ("restarting", "→ Restarting [Error Recovery]"),
            "Characters_Full": ("sell_characters", "→ Sell Characters"),
            "SellAccsesurry": ("sell_accsesurry", "→ Sell Accessory"),
            "HardStory": ("hardstory", "→ Hard Story"),
            "SideStory": ("sidestory", "→ Side Story"),
            "Sub-Stores": ("substories", "→ Sub Stories"),
            "CheckSubStoriesAllCleared": ("substories_check", "→ Sub Stories Check"),
            "Character_Slots_Purchase_Tasks": ("character_slots_purchase", "→ Character Slots Purchase"),
            "Recive_Gold_From_Box_For_Characters_Purchase_Tasks": ("recive_gold_from_box_for_characters_purchase", "→ Receive Gold From Box For Characters Purchase"),
            "Exchange_Gold_Characters_Tasks": ("exchange_gold_characters", "→ Exchange Gold Characters"),
            "Recive_GiftBox_Tasks": ("recive_giftbox", "→ Receive Gift Box"),
            "Recive_GiftBox_Check_Tasks": ("recive_giftbox_check", "→ Receive Gift Box Check"),
            "Recive_Giftbox_Orbs_Check_Tasks": ("recive_giftbox_orbs_check", "→ Receive Gift Box Orbs Check"),
            "Skip_Kon_Bonaza_Tasks": ("skip_kon_bonaza", "→ Skip Kon Bonanza"),
            "Kon_Bonaza_1Match_Tasks": ("kon_bonaza_1match_tasks", "→ Kon Bonaza 1 Match Tasks"),
            "Skip_Yukio_Event_Tasks": ("skip_yukio_event", "→ Skip Yukio Event"),
            "Sort_Characters_Lowest_Level_Tasks": ("sort_characters_lowest_level", "→ Sort Characters Lowest Level"),
            "Sort_Filter_Ascension_Tasks": ("sort_filter_ascension", "→ Sort Filter Ascension"),
            "Sort_Multi_Select_Garbage_First_Tasks": ("sort_multi_select_garbage_first", "→ Sort Multi Select Garbage First"),
            "Upgrade_Characters_Level_Tasks": ("upgrade_characters_level", "→ Upgrade Characters Level"),
            "Upgrade_Characters_Back_To_Edit_Tasks": ("upgrade_characters_back_to_edit", "→ Upgrade Characters Back To Edit"),
            "Recive_Giftbox_Orbs_Tasks": ("recive_giftbox_orbs", "→ Receive Gift Box Orbs"),
            "Reroll_Earse_GameData_Tasks": ("reroll_earse_gamedata", "→ Reroll Erase Game Data"),
            "Reroll_Earse_GameDataPart2_Tasks": ("reroll_earse_gamedatapart2", "→ Reroll Erase Game Data Part 2"),
            "Reroll_Tutorial_FirstMatch_Tasks": ("reroll_tutorial_firstmatch", "→ Reroll Tutorial First Match"),
            "Reroll_Tutorial_CharacterChoose_Tasks": ("reroll_tutorial_characterchoose", "→ Reroll Tutorial Character Choose"),
            "Reroll_Tutorial_CharacterChoosePart2_Tasks": ("reroll_tutorial_characterchoosepart2", "→ Reroll Tutorial Character Choose Part 2"),
            "Reroll_Tutorial_SecondMatch_Tasks": ("reroll_tutorial_secondmatch", "→ Reroll Tutorial Second Match"),
            "Reroll_ReplaceIchigoWithFiveStar_Tasks": ("reroll_replaceichigowithfivestar", "→ Reroll Replace Ichigo"),
            "NextTaskSet_Tasks": ("next_task_progression", "→ Next Task Set"),
            "ScreenShot_MainMenu_Tasks": ("main_screenshot", "→ Screenshot Main Menu"),
            "Extract_Orb_Count_Tasks": ("extract_orb_counts", "→ Extract Orb Count"),
            "Extract_Account_ID_Tasks": ("extract_account_id", "→ Extract Account ID"),
            "Login1_Prepare_For_Link_Tasks": ("login1_prepare_for_link", "→ Prepare for Link"),
            "Login2_Klab_Login_Tasks": ("login2_klab_login", "→ KLAB Login"),
            "Login3_Wait_For_2FA_Tasks": ("login3_wait_for_2fa", "→ Wait for 2FA"),
            "Login4_Confirm_Link_Tasks": ("login4_confirm_link", "→ Confirm Link"),
            "BackToMain_Tasks": ("main", "→ Main")
        }
        
        # Handle NextTaskSet_Tasks flag - triggers progression to next task set
        if task.get("NextTaskSet_Tasks", False):
            current_task_set = self.process_monitor.active_task_set.get(device_id, "restarting")
            recommended_mode = device_state_manager.get_next_task_set_after_restarting(device_id)
            # Only switch if we're actually changing to a different task set
            if recommended_mode != current_task_set:
                print(f"[{device_id}] Task set progression: {current_task_set} → {recommended_mode}")
                self.process_monitor.set_active_tasks(device_id, recommended_mode)
                # Reset action tracking when switching task sets
                self.process_monitor.reset_action_tracking(device_id)
            else:
                print(f"[{device_id}] Already in task set: {recommended_mode}")
            return
        
        # BackToStory flag - works from ANY task set to determine next progression
        if task.get("BackToStory", False):
            current_task_set = self.process_monitor.active_task_set.get(device_id, "restarting")
            # Use device state manager to determine next appropriate task set
            recommended_mode = device_state_manager.get_next_task_set_after_restarting(device_id)
            if recommended_mode != current_task_set:
                print(f"[{device_id}] [BackToStory] {current_task_set} Complete → {recommended_mode}")
                self.process_monitor.set_active_tasks(device_id, recommended_mode)
                # Clear the action tracking to prevent re-triggering
                self.process_monitor.reset_action_tracking(device_id)
            else:
                print(f"[{device_id}] [BackToStory] Already in recommended task set: {recommended_mode}")
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
        
        # Handle SetFlag_ flags for sequential task execution
        for key, value in task.items():
            if key.startswith("SetFlag_") and value:
                flag_name = key.replace("SetFlag_", "")
                device_state_manager.update_state(device_id, flag_name, 1)
                print(f"[{device_id}] ✅ Flag set: {flag_name} = 1")
        
        # Handle ClearFlag_ flags for restart recovery
        for key, value in task.items():
            if key.startswith("ClearFlag_") and value:
                flag_name = key.replace("ClearFlag_", "")
                device_state_manager.update_state(device_id, flag_name, 0)
                print(f"[{device_id}] 🔄 Flag cleared: {flag_name} = 0 (restart recovery)")
        
        # Handle close_brave flag to terminate Brave browser
        if task.get("close_brave", False):
            print(f"[{device_id}] 🔴 Closing Brave browser...")
            await run_adb_command("shell am force-stop com.brave.browser", device_id)
            await asyncio.sleep(1.0)  # Small delay after closing
            print(f"[{device_id}] ✅ Brave browser closed")
        
        # Handle close_game flag to terminate game process
        if task.get("close_game", False):
            print(f"[{device_id}] 🔴 Closing Bleach game...")
            await run_adb_command(f"shell am force-stop {BLEACH_PACKAGE_NAME}", device_id)
            await asyncio.sleep(1.0)  # Small delay after closing
            print(f"[{device_id}] ✅ Bleach game closed")
        
        # Handle First_Match_Script flag to run tutorial automation
        if task.get("First_Match_Script", False):
            print(f"[{device_id}] 🎮 First Match Script detected - executing tutorial script...")
            try:
                from logical_process import run_first_match_script
                await run_first_match_script(device_id)
                print(f"[{device_id}] ✅ First Match Script completed")
            except Exception as e:
                print(f"[{device_id}] ❌ Error running First Match Script: {e}")
        
        # Handle HardModeSwipe flag to run hard mode automation
        if task.get("HardModeSwipe", False):
            print(f"[{device_id}] 🎮 Hard Mode Swipe detected - executing swipe sequence...")
            try:
                from logical_process import run_hard_mode_swipes
                await run_hard_mode_swipes(device_id)
                print(f"[{device_id}] ✅ Hard Mode Swipe completed")
            except Exception as e:
                print(f"[{device_id}] ❌ Error running Hard Mode Swipe: {e}")

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
                
                # Execute the click if not a detection-only task
                if task.get("click_location_str") != "0,0" and "[Multi:" not in task_name and "[Executed" not in task_name:
                    await self.execute_tap_with_offset(device_id, task["click_location_str"], task)
                    
                    # Handle text input flags after clicking
                    await self.handle_text_input_flags(device_id, task)
                    
                    # Handle task flags AFTER execution for action tasks
                    await self.handle_task_flags(device_id, task)
                else:
                    # For detection-only tasks (0,0 click), handle flags immediately
                    await self.handle_task_flags(device_id, task)
                
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
                    
                    # Execute the click if not a detection-only task
                    if task.get("click_location_str") != "0,0" and "[Executed" not in task_name:
                        await self.execute_tap_with_offset(device_id, task["click_location_str"], task)
                        
                        # Handle text input flags after clicking
                        await self.handle_text_input_flags(device_id, task)
                        
                        # Handle task flags AFTER execution for action tasks
                        await self.handle_task_flags(device_id, task)
                    else:
                        # For detection-only tasks (0,0 click), handle flags immediately
                        await self.handle_task_flags(device_id, task)
                    
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
        """Check if device should be sleeping (not processing tasks)"""
        current_time = time.time()
        return current_time < self.device_sleep_until.get(device_id, 0)
    
    def is_text_input_active(self, device_id: str) -> bool:
        """Check if text input is currently active (should pause all other tasks)"""
        current_time = time.time()
        return current_time < self.text_input_active.get(device_id, 0)
    
    async def watch_device_optimized(self, device_id: str) -> Optional[str]:
        """Optimized device watching with smart multi-detection and state tracking"""
        print(f"[{device_id}] Starting monitoring...")
        print(f"[{device_id}] {device_state_manager.get_progress_summary(device_id)}")
        
        self.device_states[device_id] = {'stable_count': 0, 'last_action': time.time()}
        self.no_action_timers[device_id] = time.time()
        self.last_endgame_check = getattr(self, 'last_endgame_check', 0)
        self.fetch_in_progress = getattr(self, 'fetch_in_progress', False)
        self.last_successful_fetch = getattr(self, 'last_successful_fetch', 0)
        
        while not self.stop_event.is_set():
            try:
                # Check if all devices are linked periodically (every 10 seconds)
                # BUT ONLY if not already fetching and hasn't fetched recently
                current_time = time.time()
                if (current_time - self.last_endgame_check > 10 and 
                    not self.fetch_in_progress and 
                    current_time - self.last_successful_fetch > 300):  # Wait 5 minutes between fetches
                    
                    self.last_endgame_check = current_time
                    
                    # Check if all devices have isLinked = 1
                    from airtable_stock_fetcher import check_and_fetch_all_accounts
                    all_linked = True
                    linked_count = 0
                    # Check using the actual device IDs (IP addresses) from settings
                    for actual_device_id in settings.DEVICE_IDS:
                        state = device_state_manager.get_state(actual_device_id)
                        is_linked = state.get("isLinked", 0)
                        
                        # Debug: Show what we're checking
                        if current_time % 60 < 10:  # Log once per minute
                            device_name = device_state_manager._get_device_name(actual_device_id)
                            print(f"[DEBUG] {device_name}: isLinked={is_linked}, state keys={list(state.keys())[:5]}")
                        
                        if is_linked == 1:  # Explicitly check for 1, not truthy
                            linked_count += 1
                        else:
                            all_linked = False
                            # Don't break, count all linked devices
                    
                    # Debug log every minute
                    if current_time % 60 < 10 and linked_count > 0:  # Log once per minute if any linked
                        device_name = device_state_manager._get_device_name(device_id)
                        print(f"[{device_name}] Link status check: {linked_count}/10 devices linked")
                    
                    if all_linked and not self.fetch_in_progress:
                        print(f"[{device_id}] 🎉 All accounts linked! Starting fetch process...")
                        
                        # SET FLAG TO PREVENT MULTIPLE TRIGGERS
                        self.fetch_in_progress = True
                        
                        try:
                            # STEP 1: Stop all monitoring to prevent auto-generation
                            print(f"[ALL DEVICES] ⏸️ Pausing all monitoring...")
                            device_state_manager.fetch_mode = True  # Prevent auto-generation
                            await asyncio.sleep(1)
                            
                            # STEP 2: Close all games
                            print(f"[ALL DEVICES] 🔴 Closing games...")
                            for actual_device_id in settings.DEVICE_IDS:
                                await run_adb_command(f"shell am force-stop {BLEACH_PACKAGE_NAME}", actual_device_id)
                            
                            # STEP 3: Wait for games to fully close
                            print(f"[ALL DEVICES] ⏳ Waiting for games to close...")
                            await asyncio.sleep(3)
                            
                            # STEP 4: Fetch new accounts and recreate device files
                            print(f"[ALL DEVICES] 📥 Fetching new accounts from Airtable...")
                            result = await check_and_fetch_all_accounts()
                            
                            # STEP 5: Wait for file operations to complete
                            await asyncio.sleep(2)
                            
                            if result:
                                print(f"[ALL DEVICES] ✅ New accounts fetched! Starting reroll cycle...")
                                
                                # STEP 6: Set ALL devices to first reroll task
                                for actual_device_id in settings.DEVICE_IDS:
                                    self.process_monitor.set_active_tasks(actual_device_id, "reroll_earse_gamedata")
                                
                                # STEP 7: Launch all games
                                print(f"[ALL DEVICES] 🚀 Launching games...")
                                for actual_device_id in settings.DEVICE_IDS:
                                    await self.process_monitor.launch_bleach(actual_device_id)
                                    await asyncio.sleep(0.5)  # Small delay between launches
                                
                                # Mark successful fetch
                                self.last_successful_fetch = current_time
                            else:
                                print(f"[ALL DEVICES] ❌ Failed to fetch accounts")
                        
                        finally:
                            # ALWAYS reset flags
                            self.fetch_in_progress = False
                            device_state_manager.fetch_mode = False  # Re-enable auto-generation
                            print(f"[ALL DEVICES] ▶️ Resuming monitoring...")
                
                # Skip all monitoring during fetch mode
                if self.fetch_in_progress or getattr(device_state_manager, 'fetch_mode', False):
                    await asyncio.sleep(1)
                    continue
                
                if self.is_device_sleeping(device_id):
                    await asyncio.sleep(0.1)
                    continue
                
                # Check if text input is active - pause all other tasks
                if self.is_text_input_active(device_id):
                    await asyncio.sleep(0.5)
                    continue
                
                self.frame_processed_tasks[device_id].clear()
                
                if time.time() - self.no_action_timers.get(device_id, time.time()) > 240:
                    print(f"[{device_id}] 240s timeout - restarting")
                    await self.process_monitor.kill_and_restart_game(device_id)
                    self.no_action_timers[device_id] = time.time()
                
                if self.process_monitor.should_check_process(device_id):
                    is_bleach_running = await self.process_monitor.is_bleach_running(device_id)
                    
                    if self.process_monitor.is_initial_setup_needed(device_id):
                        if not is_bleach_running:
                            print(f"[{device_id}] Game not running, launching...")
                            await self.process_monitor.launch_bleach(device_id)
                            # Check if we should go to reroll tasks or restarting tasks
                            next_task_set = device_state_manager.get_next_task_set_after_restarting(device_id)
                            # If reroll tasks are needed, go directly to them, otherwise use restarting
                            if next_task_set.startswith("reroll_"):
                                print(f"[{device_id}] Incomplete reroll tasks detected, switching to: {next_task_set}")
                                self.process_monitor.set_active_tasks(device_id, next_task_set)
                            else:
                                self.process_monitor.set_active_tasks(device_id, "restarting")
                            device_state_manager.increment_counter(device_id, "RestartingCount")
                        else:
                            # Game is already running - only set initial task on first setup
                            current_task_set = self.process_monitor.active_task_set.get(device_id, None)
                            if current_task_set is None:
                                # First time setup - set initial task based on device state
                                recommended_mode = device_state_manager.should_skip_to_mode(device_id)
                                print(f"[{device_id}] Initial setup: Setting task set to {recommended_mode}")
                                self.process_monitor.set_active_tasks(device_id, recommended_mode)
                        
                        self.process_monitor.mark_initial_complete(device_id)
                    
                    elif not is_bleach_running:
                        print(f"[{device_id}] Game crashed, re-launching...")
                        await self.process_monitor.launch_bleach(device_id)
                        # Check if we should go to reroll tasks or restarting tasks
                        next_task_set = device_state_manager.get_next_task_set_after_restarting(device_id)
                        # If reroll tasks are needed, go directly to them, otherwise use restarting
                        if next_task_set.startswith("reroll_"):
                            print(f"[{device_id}] Incomplete reroll tasks detected, switching to: {next_task_set}")
                            self.process_monitor.set_active_tasks(device_id, next_task_set)
                        else:
                            self.process_monitor.set_active_tasks(device_id, "restarting")
                        device_state_manager.increment_counter(device_id, "RestartingCount")
                
                # REMOVED: Automatic task progression logic that was causing infinite switching
                # Task progression should ONLY happen through flags (BackToStory, NextTaskSet_Tasks, etc.)
                # This prevents premature switching before tasks complete their objectives
                
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
        
        return True
    
    def robust_number_ocr_cleanup(self, device_id: str, ocr_result: str) -> str:
        """
        Robust OCR cleanup specifically for numbers - handles common OCR character errors
        PRESERVES original comma positioning since screen numbers always have commas
        """
        try:
            if not ocr_result or not isinstance(ocr_result, str):
                return "0"
            
            # Clean the raw result
            raw_orb = ocr_result.strip()
            print(f"[{device_id}] 🔍 Raw OCR: '{raw_orb}'")
            
            # Handle specific known complete misreadings first
            known_fixes = {
                # Common "2X,1X4" → "2,1X4" pattern (missing digit in thousands)
                "202,100": "20,210",
                "203,100": "20,310", 
                "204,100": "20,410",
                "205,100": "20,510",
                "206,100": "20,610",
                "207,100": "20,710",
                "208,100": "20,810",
                "209,100": "20,910",
                "21,100": "21,110",
                "21,200": "21,120",
                "21,300": "21,130",
                "21,400": "21,140",
                "21,500": "21,150",
                
                # Common "X,1XX" → "XX,1XX" pattern (missing leading digit)  
                "2,153": "21,153",
                "2,134": "21,134",
                "2,145": "21,145",
                "1,234": "11,234",
                "1,567": "15,567",
                "3,456": "34,456",
                
                # Common swapped digit patterns
                "12,143": "21,134",
                "13,124": "31,124",
                "14,123": "41,123"
            }
            
            if raw_orb in known_fixes:
                result = known_fixes[raw_orb]
                print(f"[{device_id}] 🔧 Applied known fix: {raw_orb} → {result}")
                return result
            
            # Fix common character misreadings while preserving comma position
            result = raw_orb
            
            # Character-by-character fixes (but preserve comma and structure)
            char_fixes = {
                'O': '0', 'o': '0',     # O/o -> 0
                'l': '1', 'I': '1',     # l/I -> 1  
                'S': '5', 's': '5',     # S/s -> 5
                'g': '9',               # g -> 9
                'G': '6',               # G -> 6
                'B': '8', 'b': '8',     # B/b -> 8
                'D': '0',               # D -> 0
                'Z': '2', 'z': '2',     # Z/z -> 2
                'A': '4',               # A -> 4
                'T': '7',               # T -> 7
                'E': '3',               # E -> 3
            }
            
            for wrong_char, correct_char in char_fixes.items():
                result = result.replace(wrong_char, correct_char)
            
            # Remove any spaces but keep comma structure
            result = result.replace(' ', '')
            
            # If result doesn't look like a number with comma, return original
            if not (',' in result and len(result.replace(',', '')) >= 3):
                print(f"[{device_id}] ⚠️ Result doesn't look like number, keeping original")
                result = raw_orb
            
            print(f"[{device_id}] 🎯 Final result: {raw_orb} → {result}")
            return result
            
        except Exception as e:
            print(f"[{device_id}] ❌ OCR cleanup error: {e}")
            return ocr_result  # Return original if cleanup fails
    
    def store_multi_orb_attempt(self, device_id: str, attempt_num: int, ocr_result: str):
        """Store multiple orb attempts for intelligent consensus"""
        if device_id not in self.orb_multi_attempts:
            self.orb_multi_attempts[device_id] = {}
        
        # Clean the result using robust cleanup
        cleaned_result = self.robust_number_ocr_cleanup(device_id, ocr_result)
        self.orb_multi_attempts[device_id][attempt_num] = {
            'raw': ocr_result,
            'cleaned': cleaned_result
        }
        print(f"[{device_id}] 📝 Orb attempt {attempt_num}: '{ocr_result}' → '{cleaned_result}'")
    
    def get_best_orb_consensus(self, device_id: str) -> str:
        """Get the best orb value from multiple attempts using intelligent consensus"""
        if device_id not in self.orb_multi_attempts:
            return None
        
        attempts = self.orb_multi_attempts[device_id]
        
        # Enhanced validation and scoring system
        scored_results = []
        
        for attempt_num, attempt_data in attempts.items():
            raw = attempt_data['raw']
            cleaned = attempt_data['cleaned']
            
            # Score each result based on quality indicators
            score = 0
            
            # Basic format check (has comma and reasonable length)
            if ',' in cleaned and len(cleaned.replace(',', '')) >= 3:
                score += 10
            
            # Digit pattern validation (should be mostly digits and comma)
            digit_ratio = len([c for c in cleaned if c.isdigit() or c == ',']) / max(len(cleaned), 1)
            if digit_ratio >= 0.8:
                score += 15
                
            # Length reasonableness (orb counts usually 4-7 characters including comma)
            if 4 <= len(cleaned) <= 7:
                score += 10
                
            # Comma position check (should be exactly 3 digits after comma)
            if ',' in cleaned:
                comma_pos = cleaned.find(',')
                digits_after_comma = len(cleaned) - comma_pos - 1
                # Comma should have exactly 3 digits after it (like 1,234 or 21,573)
                if digits_after_comma == 3:
                    score += 15
                else:
                    score -= 10  # Penalize wrong comma position
            
            # Penalize obviously wrong patterns
            if len(cleaned.replace(',', '')) < 3:  # Too short
                score -= 20
            if len(cleaned.replace(',', '')) > 8:   # Too long  
                score -= 15
            if cleaned.count(',') > 1:  # Multiple commas
                score -= 25
            if cleaned.count(',') == 0:  # No comma at all
                score -= 15
            
            # Special penalty for clearly wrong patterns
            if cleaned in ["21,1345", "2,1573", "211,345"]:  # Known bad patterns
                score -= 50
                
            scored_results.append({
                'attempt': attempt_num,
                'raw': raw,
                'cleaned': cleaned,
                'score': score
            })
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"[{device_id}] 🔍 Scored attempts:")
        for result in scored_results:
            print(f"[{device_id}]   #{result['attempt']}: '{result['raw']}' → '{result['cleaned']}' (score: {result['score']})")
        
        # Count frequency of top-scored results
        value_counts = {}
        valid_results = [r for r in scored_results if r['score'] > 0]
        
        for result in valid_results:
            cleaned = result['cleaned']
            value_counts[cleaned] = value_counts.get(cleaned, 0) + 1
        
        print(f"[{device_id}] 📊 Valid value frequencies: {value_counts}")
        
        if not value_counts:
            print(f"[{device_id}] ⚠️ No valid results found")
            del self.orb_multi_attempts[device_id]
            return None
        
        # Smart consensus logic
        best_value = None
        
        # If we have a clear winner (appears multiple times)
        most_frequent = max(value_counts, key=value_counts.get)
        frequency = value_counts[most_frequent]
        
        if frequency >= 2:
            best_value = most_frequent
            reason = f"appeared {frequency} times"
        elif len(value_counts) == 1:
            # Only one valid result
            best_value = most_frequent
            reason = "only valid result"
        else:
            # Multiple different results - pick highest scored one
            best_scored = scored_results[0]
            if best_scored['score'] >= 20:  # High confidence threshold
                best_value = best_scored['cleaned']
                reason = f"highest score ({best_scored['score']})"
        
        if best_value:
            print(f"[{device_id}] 🎯 Consensus winner: '{best_value}' ({reason})")
            del self.orb_multi_attempts[device_id]
            return best_value
        else:
            print(f"[{device_id}] ❌ No reliable consensus found")
            del self.orb_multi_attempts[device_id]
            return None
    
    def robust_account_id_cleanup(self, device_id: str, ocr_result: str) -> str:
        """
        Robust Account ID cleanup - handles common OCR character errors
        Account IDs are usually numeric strings (like "12345678901")
        """
        try:
            if not ocr_result or not isinstance(ocr_result, str):
                return ""
            
            # Clean the raw result
            raw_id = ocr_result.strip()
            print(f"[{device_id}] 🔍 Raw Account ID OCR: '{raw_id}'")
            
            # Fix common character misreadings for account IDs
            result = raw_id
            
            # Character-by-character fixes
            char_fixes = {
                'O': '0', 'o': '0',     # O/o -> 0
                'l': '1', 'I': '1',     # l/I -> 1  
                'S': '5', 's': '5',     # S/s -> 5
                'g': '9',               # g -> 9
                'G': '6',               # G -> 6
                'B': '8', 'b': '8',     # B/b -> 8
                'D': '0',               # D -> 0
                'Z': '2', 'z': '2',     # Z/z -> 2
                'A': '4',               # A -> 4
                'T': '7',               # T -> 7
                'E': '3',               # E -> 3
            }
            
            for wrong_char, correct_char in char_fixes.items():
                result = result.replace(wrong_char, correct_char)
            
            # Remove any spaces and non-numeric characters except digits
            result = ''.join(c for c in result if c.isdigit())
            
            # Account IDs should be numeric and reasonably long (usually 8-15 digits)
            if len(result) < 5:
                print(f"[{device_id}] ⚠️ Account ID too short, keeping original")
                result = raw_id
            elif len(result) > 20:
                print(f"[{device_id}] ⚠️ Account ID too long, truncating")
                result = result[:15]  # Keep first 15 digits
            
            print(f"[{device_id}] 🎯 Account ID result: {raw_id} → {result}")
            return result
            
        except Exception as e:
            print(f"[{device_id}] ❌ Account ID cleanup error: {e}")
            return ocr_result  # Return original if cleanup fails
    
    def store_account_id_attempt(self, device_id: str, attempt_num: int, ocr_result: str):
        """Store account ID extraction attempt for consensus checking"""
        if device_id not in self.account_id_attempts:
            self.account_id_attempts[device_id] = {}
        
        # Clean the result (remove extra spaces, fix common OCR errors)
        cleaned_result = ocr_result.strip().replace("  ", " ").replace("O", "0").replace("o", "0").replace("l", "1").replace("I", "1")
        self.account_id_attempts[device_id][attempt_num] = cleaned_result
        print(f"[{device_id}] Account ID attempt {attempt_num}/4: '{cleaned_result}'")
    
    def check_account_id_consensus(self, device_id: str):
        """Check if there's consensus among account ID extraction attempts"""
        if device_id not in self.account_id_attempts:
            return None
        
        attempts = self.account_id_attempts[device_id]
        
        # Count occurrences of each value
        value_counts = {}
        for attempt_num, value in attempts.items():
            if value and value.strip() and len(value.strip()) > 5:  # Only count non-empty values with reasonable length
                value_counts[value] = value_counts.get(value, 0) + 1
        
        # Find values that appear 2 or more times
        consensus_candidates = [value for value, count in value_counts.items() if count >= 2]
        
        if consensus_candidates:
            # Return the most frequent value
            consensus_value = max(consensus_candidates, key=lambda x: value_counts[x])
            print(f"[{device_id}] Account ID extraction attempts: {attempts}")
            print(f"[{device_id}] Value counts: {value_counts}")
            print(f"[{device_id}] Consensus value: '{consensus_value}' (appeared {value_counts[consensus_value]} times)")
            
            # Clear attempts after consensus
            self.account_id_attempts[device_id] = {}
            return consensus_value
        else:
            print(f"[{device_id}] No Account ID consensus - all attempts different: {attempts}")
            # Clear attempts after failed consensus
            self.account_id_attempts[device_id] = {}
            return None
        
    async def run_monitoring_cycle(self): 
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
                        if self.process_monitor.should_check_process(device_id):
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
                    if not self.is_device_sleeping(device_id) and not self.is_text_input_active(device_id)
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