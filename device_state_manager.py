# device_state_manager.py - Enhanced with new account management and task progression
import json
import os
from typing import Dict, Any
from datetime import datetime
import asyncio
from threading import Lock

# Timezone support
try:
    import pytz
    ISTANBUL_TZ = pytz.timezone('Europe/Istanbul')
    TIMEZONE_AVAILABLE = True
except ImportError:
    print("[TIMEZONE] pytz not available, falling back to system timezone")
    TIMEZONE_AVAILABLE = False
    ISTANBUL_TZ = None

class DeviceStateManager:
    """Manages persistent state for each device including account info and task progression"""
    
    def __init__(self):
        self.states: Dict[str, Dict[str, Any]] = {}
        self.state_dir = "device_states"
        self.locks: Dict[str, Lock] = {}
        self.device_mapping = {
            "127.0.0.1:16800": "DEVICE1",
            "127.0.0.1:16832": "DEVICE2",
            "127.0.0.1:16864": "DEVICE3",
            "127.0.0.1:16896": "DEVICE4",
            "127.0.0.1:16928": "DEVICE5",
            "127.0.0.1:16960": "DEVICE6",
            "127.0.0.1:16992": "DEVICE7",
            "127.0.0.1:17024": "DEVICE8",
            "127.0.0.1:17056": "DEVICE9",
            "127.0.0.1:17088": "DEVICE10"
        }
        
        # Create reverse mapping (DEVICE1 -> IP address)
        self.reverse_mapping = {v: k for k, v in self.device_mapping.items()}
        
        # Flag to prevent auto-generation during fetch
        self.fetch_mode = False
        
        # Create state directory if it doesn't exist
        os.makedirs(self.state_dir, exist_ok=True)
        
        # Initialize states for all devices
        self._initialize_all_devices()
        
        # Initialize stock management
        self._initialize_stock_file()
    
    def _get_istanbul_time(self) -> str:
        """Get current time in Istanbul timezone as ISO string"""
        if TIMEZONE_AVAILABLE and ISTANBUL_TZ:
            # Get current UTC time and convert to Istanbul timezone
            utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
            istanbul_time = utc_now.astimezone(ISTANBUL_TZ)
            return istanbul_time.isoformat()
        else:
            # Fallback to system timezone
            return datetime.now().isoformat()
    
    def _get_device_name(self, device_id: str) -> str:
        """Get device name from device ID"""
        # If it's already a DEVICE name (DEVICE1, DEVICE2, etc.), return as is
        if device_id.startswith("DEVICE") and device_id[6:].isdigit():
            return device_id
        # Otherwise, look it up in the mapping
        return self.device_mapping.get(device_id, f"DEVICE_{device_id.replace(':', '_')}")
    
    def _get_state_file_path(self, device_name: str) -> str:
        """Get the JSON file path for a device"""
        return os.path.join(self.state_dir, f"{device_name}.json")
    
    def _get_default_state(self) -> Dict[str, Any]:
        """Get default state structure for a new device"""
        return {
            "AccountID": "",
            "UserName": "Player",
            "Email": "",
            "Password": "",
            "isLinked": 0,
            "Orbs": "0",
            "RestartingCount": 0,
            "Reroll_Earse_GameData": 0,
            "Reroll_Earse_GameDataPart2": 0,
            "Reroll_Tutorial_FirstMatch": 0,
            "Reroll_Tutorial_CharacterChoose": 0,
            "Reroll_Tutorial_CharacterChoosePart2": 0,
            "Reroll_Tutorial_SecondMatch": 0,
            "Reroll_ReplaceIchigoWithFiveStar": 0,
            "EasyMode": 0,
            "HardMode": 0,
            "SideMode": 0,
            "SubStory": 0,
            "Character_Slots_Purchased": 0,
            "Exchange_Gold_Characters": 0,
            "Recive_GiftBox": 0,
            "Skip_Kon_Bonaza_100Times": 0,
            "Skip_Kon_Bonaza": 0,
            "Character_Slots_Count": 0,
            "ScreenShot_MainMenu": 0,
            "Skip_Yukio_Event": 0,
            "Skip_Yukio_Event_Retry_Count": 0,
            "Sort_Characters_Lowest_Level": 0,
            "Sort_Filter_Ascension": 0,
            "Sort_Multi_Select_Garbage_First": 0,
            "Upgrade_Characters_Level": 0,
            "Recive_Giftbox_Orbs": 0,
            "Login1_Prepare_Link": 0,
            "Account_Linked": 0,
            "Login2_Email_Done": 0,
            "Login2_Password_Done": 0,
            "Login2_Cloudflare_Done": 0,
            "synced_to_airtable": False,
            "LastUpdated": self._get_istanbul_time(),
            "CurrentTaskSet": "restarting",
            "SessionStats": {
                "SessionStartTime": self._get_istanbul_time(),
                "TasksExecuted": 0,
                "LastTaskExecuted": None
            }
        }
    
    def _initialize_all_devices(self):
        """Initialize state files for all configured devices"""
        for device_id in self.device_mapping.keys():
            device_name = self._get_device_name(device_id)
            self.locks[device_id] = Lock()
            
            # Load or create state file
            state_file = self._get_state_file_path(device_name)
            
            if os.path.exists(state_file):
                try:
                    with open(state_file, 'r') as f:
                        loaded_state = json.load(f)
                    
                    # Migrate old states - remove SubStory sub-keys if they exist
                    keys_to_remove = [
                        "SubStory-TheHumanWorld",
                        "SubStory-TheSoulSociety", 
                        "SubStory-HuecoMundo",
                        "SubStory-TheFutureSociety",
                        "SubStory-Others"
                    ]
                    
                    for key in keys_to_remove:
                        if key in loaded_state:
                            del loaded_state[key]
                    
                    # Ensure all required keys exist (for backward compatibility)
                    default_state = self._get_default_state()
                    for key, value in default_state.items():
                        if key not in loaded_state:
                            loaded_state[key] = value
                    
                    self.states[device_id] = loaded_state
                    print(f"[STATE] Loaded existing state for {device_name}")
                except Exception as e:
                    print(f"[STATE] Error loading state for {device_name}: {e}")
                    if not self.fetch_mode:  # Only auto-generate if not in fetch mode
                        self.states[device_id] = self._get_default_state()
                        self._save_state(device_id)
            else:
                if not self.fetch_mode:  # Only auto-generate if not in fetch mode
                    self.states[device_id] = self._get_default_state()
                    self._save_state(device_id)
                    print(f"[STATE] Created new state file for {device_name}")
    
    def _save_state(self, device_id: str):
        """Save device state to JSON file"""
        device_name = self._get_device_name(device_id)
        state_file = self._get_state_file_path(device_name)
        
        try:
            self.states[device_id]["LastUpdated"] = self._get_istanbul_time()
            with open(state_file, 'w') as f:
                json.dump(self.states[device_id], f, indent=2)
        except Exception as e:
            print(f"[STATE] Error saving state for {device_name}: {e}")
    
    def get_state(self, device_id: str) -> Dict[str, Any]:
        """Get current state for a device"""
        # If it's a DEVICE name, convert to IP address
        if device_id.startswith("DEVICE") and device_id[6:].isdigit():
            # Look up the IP address for this device name
            actual_device_id = self.reverse_mapping.get(device_id, device_id)
        else:
            actual_device_id = device_id
        
        if actual_device_id not in self.states:
            if not self.fetch_mode:  # Only auto-generate if not in fetch mode
                self.states[actual_device_id] = self._get_default_state()
            else:
                return {}  # Return empty state during fetch mode
        return self.states.get(actual_device_id, {}).copy()
    
    def update_state(self, device_id: str, key: str, value: Any):
        """Update a specific state value for a device"""
        # If it's a DEVICE name, convert to IP address
        if device_id.startswith("DEVICE") and device_id[6:].isdigit():
            # Look up the IP address for this device name
            actual_device_id = self.reverse_mapping.get(device_id, device_id)
        else:
            actual_device_id = device_id
        
        with self.locks.get(actual_device_id, Lock()):
            if actual_device_id not in self.states:
                self.states[actual_device_id] = self._get_default_state()
            
            self.states[actual_device_id][key] = value
            self._save_state(actual_device_id)
    
    def set_json_flag(self, device_id: str, flag_name: str, value: Any = 1):
        """Set a JSON flag based on task detection"""
        # Map json_ prefixed flags to actual state keys
        flag_mapping = {
            "json_EasyMode": "EasyMode",
            "json_HardMode": "HardMode",
            "json_SideMode": "SideMode",
            "json_SubStory": "SubStory",
            "json_Character_Slots_Purchased": "Character_Slots_Purchased",
            "json_Exchange_Gold_Characters": "Exchange_Gold_Characters",
            "json_Recive_GiftBox": "Recive_GiftBox",
            "json_ScreenShot_MainMenu": "ScreenShot_MainMenu",
            "json_Kon_Bonaza": "Skip_Kon_Bonaza",
            "json_Skip_Yukio_Event": "Skip_Yukio_Event",
            "json_Sort_Characters_Lowest_Level": "Sort_Characters_Lowest_Level",
            "json_Sort_Filter_Ascension": "Sort_Filter_Ascension",
            "json_Sort_Multi_Select_Garbage_First": "Sort_Multi_Select_Garbage_First",
            "json_Upgrade_Characters_Level": "Upgrade_Characters_Level",
            "json_Recive_Giftbox_Orbs": "Recive_Giftbox_Orbs",
            "json_Login1_Prepare_Link": "Login1_Prepare_Link",
            "json_Account_Linked": "Account_Linked",
            "json_Login2_Email_Done": "Login2_Email_Done",
            "json_Login2_Password_Done": "Login2_Password_Done",
            "json_Login2_Cloudflare_Done": "Login2_Cloudflare_Done",
            "json_isLinked": "isLinked",
            # Reroll task flags
            "json_Reroll_Earse_GameData": "Reroll_Earse_GameData",
            "json_Reroll_Earse_GameDataPart2": "Reroll_Earse_GameDataPart2",
            "json_Reroll_Tutorial_FirstMatch": "Reroll_Tutorial_FirstMatch",
            "json_Reroll_Tutorial_CharacterChoose": "Reroll_Tutorial_CharacterChoose",
            "json_Reroll_Tutorial_CharacterChoosePart2": "Reroll_Tutorial_CharacterChoosePart2",
            "json_Reroll_Tutorial_SecondMatch": "Reroll_Tutorial_SecondMatch",
            "json_Reroll_ReplaceIchigoWithFiveStar": "Reroll_ReplaceIchigoWithFiveStar"
        }
        
        if flag_name in flag_mapping:
            state_key = flag_mapping[flag_name]
            self.update_state(device_id, state_key, value)
            device_name = self._get_device_name(device_id)
            print(f"[{device_name}] Set {state_key} = {value}")
    
    def increment_kon_bonaza_skip(self, device_id: str):
        """Increment Skip_Kon_Bonaza_100Times counter and set Skip_Kon_Bonaza when reaching 100"""
        with self.locks.get(device_id, Lock()):
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            current_value = self.states[device_id].get("Skip_Kon_Bonaza_100Times", 0)
            if current_value < 100:
                new_value = current_value + 1
                self.states[device_id]["Skip_Kon_Bonaza_100Times"] = new_value
                
                # Set Skip_Kon_Bonaza to 1 when reaching 100
                if new_value >= 100:
                    self.states[device_id]["Skip_Kon_Bonaza"] = 1
                
                self._save_state(device_id)
                device_name = self._get_device_name(device_id)
                print(f"[{device_name}] Kon Bonaza skips: {new_value}/100")
                
                if new_value >= 100:
                    print(f"[{device_name}] Kon Bonaza skip complete! Skip_Kon_Bonaza set to true.")
    
    def increment_character_slots_count(self, device_id: str):
        """Increment Character_Slots_Count counter and set Character_Slots_Purchased when reaching 200"""
        with self.locks.get(device_id, Lock()):
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            current_value = self.states[device_id].get("Character_Slots_Count", 0)
            new_value = current_value + 1
            self.states[device_id]["Character_Slots_Count"] = new_value
            
            # Set Character_Slots_Purchased to 1 when reaching 200
            if new_value >= 200:
                self.states[device_id]["Character_Slots_Purchased"] = 1
            
            self._save_state(device_id)
            device_name = self._get_device_name(device_id)
            print(f"[{device_name}] Character slots purchased: {new_value}/200")
            
            if new_value >= 200:
                print(f"[{device_name}] Character slots purchase complete!")
    

    def _reload_state(self, device_id: str):
        """Reload state from file to ensure fresh data (for multi-device sync)"""
        device_name = self._get_device_name(device_id)
        state_file = self._get_state_file_path(device_name)
        
        if os.path.exists(state_file):
            try:
                with open(state_file, 'r') as f:
                    loaded_state = json.load(f)
                self.states[device_id] = loaded_state
            except Exception as e:
                print(f"[STATE] Error reloading state for {device_name}: {e}")

    def increment_yukio_retry(self, device_id: str) -> int:
        """Increment Yukio Event retry counter with proper locking and state reload"""
        if device_id not in self.locks:
            self.locks[device_id] = Lock()
        
        with self.locks[device_id]:
            # Reload state to get latest data from file
            self._reload_state(device_id)
            
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            current_count = self.states[device_id].get("Skip_Yukio_Event_Retry_Count", 0)
            
            # Only increment if less than 3
            if current_count < 3:
                new_count = current_count + 1
                self.states[device_id]["Skip_Yukio_Event_Retry_Count"] = new_count
                self._save_state(device_id)
                
                device_name = self._get_device_name(device_id)
                print(f"[{device_name}] Yukio Retry incremented: {current_count} → {new_count}/3")
                
                # Check if we just hit 3
                if new_count == 3:
                    print(f"[{device_name}] ✓ Yukio 3 retries complete - Retry task will now be blocked")
                
                return new_count
            else:
                device_name = self._get_device_name(device_id)
                print(f"[{device_name}] Yukio Retry already at max (3) - not incrementing")
                return current_count

    def reset_yukio_retry(self, device_id: str):
        """Reset Yukio Event retry counter to 0 with proper locking"""
        if device_id not in self.locks:
            self.locks[device_id] = Lock()
        
        with self.locks[device_id]:
            # Reload state first
            self._reload_state(device_id)
            
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            old_count = self.states[device_id].get("Skip_Yukio_Event_Retry_Count", 0)
            self.states[device_id]["Skip_Yukio_Event_Retry_Count"] = 0
            self._save_state(device_id)
            
            device_name = self._get_device_name(device_id)
            print(f"[{device_name}] Yukio Retry counter reset: {old_count} → 0")
    
    def check_stop_support(self, device_id: str, stop_flag: str) -> bool:
        """Check if a task should be stopped based on device state"""
        
        # Ensure we have a lock for this device
        if device_id not in self.locks:
            self.locks[device_id] = Lock()
        
        with self.locks[device_id]:
            # Always get fresh state from file to avoid stale data
            self._reload_state(device_id)
            state = self.states.get(device_id, self._get_default_state())
            
            # Special conditional check for Yukio retry count
            if stop_flag == "Skip_Yukio_Event_Retry_At_3":
                retry_count = state.get("Skip_Yukio_Event_Retry_Count", 0)
                should_stop = retry_count >= 3
                device_name = self._get_device_name(device_id)
                print(f"[{device_name}] StopSupport check: Yukio retry={retry_count}/3, blocking={'YES' if should_stop else 'NO'}")
                return should_stop
            
            # Handle other flag mappings
            flag_mapping = {
                "json_EasyMode": "EasyMode",
                "json_HardMode": "HardMode",
                "json_SideMode": "SideMode",
                "json_SubStory": "SubStory",
                "json_Character_Slots_Purchased": "Character_Slots_Purchased",
                "json_Recive_GiftBox": "Recive_GiftBox",
                "json_Skip_Kon_Bonaza_Complete": "Skip_Kon_Bonaza_100Times",
                "json_Kon_Bonaza": "Skip_Kon_Bonaza",
                "json_Skip_Yukio_Event": "Skip_Yukio_Event",
                "json_Sort_Characters_Lowest_Level": "Sort_Characters_Lowest_Level",
                "json_Sort_Filter_Ascension": "Sort_Filter_Ascension",
                "json_Sort_Multi_Select_Garbage_First": "Sort_Multi_Select_Garbage_First",
                "json_Upgrade_Characters_Level": "Upgrade_Characters_Level",
                "json_Recive_Giftbox_Orbs": "Recive_Giftbox_Orbs"
            }
            
            if stop_flag in flag_mapping:
                state_key = flag_mapping[stop_flag]
                
                # Special case for Skip_Kon_Bonaza
                if stop_flag == "json_Skip_Kon_Bonaza_Complete":
                    return state.get(state_key, 0) >= 100
                
                return state.get(state_key, 0) == 1
            
            return False
    
    def increment_counter(self, device_id: str, counter_name: str):
        """Increment a counter value (Fixed for RestartingCount)"""
        # Only increment RestartingCount when game is actually restarted
        if counter_name == "RestartingCount":
            # This should only be called from kill_and_restart_game function
            pass
        
        with self.locks.get(device_id, Lock()):
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            current_value = self.states[device_id].get(counter_name, 0)
            self.states[device_id][counter_name] = current_value + 1
            self._save_state(device_id)
    
    
    def set_linked_status(self, device_id: str, is_linked: bool):
        """Set the linked status of a device account"""
        self.update_state(device_id, "isLinked", 1 if is_linked else 0)
        device_name = self._get_device_name(device_id)
        status = "linked" if is_linked else "not linked"
        print(f"[{device_name}] Account {status}")
    
    def update_account_info(self, device_id: str, account_id: str = None, username: str = None, 
                           orbs: int = None, email: str = None, password: str = None):
        """Update account information for a device"""
        with self.locks.get(device_id, Lock()):
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            if account_id is not None:
                self.states[device_id]["AccountID"] = account_id
            if username is not None:
                self.states[device_id]["UserName"] = username
            if orbs is not None:
                self.states[device_id]["Orbs"] = orbs
            if email is not None:
                self.states[device_id]["Email"] = email
            if password is not None:
                self.states[device_id]["Password"] = password
            
            self._save_state(device_id)
    
    def mark_easy_mode_complete(self, device_id: str):
        """Mark EasyMode as complete for a device"""
        self.update_state(device_id, "EasyMode", 1)
    
    def mark_hard_mode_complete(self, device_id: str):
        """Mark HardMode as complete (and EasyMode if not already)"""
        with self.locks.get(device_id, Lock()):
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            self.states[device_id]["EasyMode"] = 1
            self.states[device_id]["HardMode"] = 1
            self._save_state(device_id)
    
    def mark_side_mode_active(self, device_id: str):
        """Mark that SideMode is active (EasyMode and HardMode must be complete)"""
        with self.locks.get(device_id, Lock()):
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            self.states[device_id]["EasyMode"] = 1
            self.states[device_id]["HardMode"] = 1
            self.states[device_id]["SideMode"] = 1
            self._save_state(device_id)
    
    def get_next_task_set_after_restarting(self, device_id: str) -> str:
        """Determine next task set based on progression logic"""
        state = self.get_state(device_id)
        
        # Check reroll tasks first (these come before everything else)
        if state.get("Reroll_Earse_GameData", 0) == 0:
            return "reroll_earse_gamedata"
        
        if state.get("Reroll_Earse_GameDataPart2", 0) == 0:
            return "reroll_earse_gamedatapart2"
        
        if state.get("Reroll_Tutorial_FirstMatch", 0) == 0:
            return "reroll_tutorial_firstmatch"
        
        if state.get("Reroll_Tutorial_CharacterChoose", 0) == 0:
            return "reroll_tutorial_characterchoose"
        
        if state.get("Reroll_Tutorial_CharacterChoosePart2", 0) == 0:
            return "reroll_tutorial_characterchoosepart2"
        
        if state.get("Reroll_Tutorial_SecondMatch", 0) == 0:
            return "reroll_tutorial_secondmatch"
        
        if state.get("Reroll_ReplaceIchigoWithFiveStar", 0) == 0:
            return "reroll_replaceichigowithfivestar"
        
        # After reroll tasks, check story modes
        if state.get("EasyMode", 0) == 0 or state.get("HardMode", 0) == 0 or state.get("SideMode", 0) == 0:
            return "main"  # Stay in story mode tasks
        
        # All story modes complete, check SubStory
        if state.get("SubStory", 0) == 0:
            return "substories"
        
        # SubStory complete, check Character Slots
        if state.get("Character_Slots_Purchased", 0) == 0:
            return "character_slots_purchase"
        
        # Character Slots complete, check Exchange Gold Characters
        if state.get("Exchange_Gold_Characters", 0) == 0:
            return "exchange_gold_characters"
        
        # Exchange Gold Characters complete, check Gift Box
        if state.get("Recive_GiftBox", 0) == 0:
            return "recive_giftbox"
        
        # Gift Box complete, check Sort Characters Lowest Level
        if state.get("Sort_Characters_Lowest_Level", 0) == 0:
            return "sort_characters_lowest_level"
        
        # Sort Characters complete, check Sort Filter Ascension
        if state.get("Sort_Filter_Ascension", 0) == 0:
            return "sort_filter_ascension"
        
        # Sort Filter Ascension complete, check Sort Multi Select Garbage First
        if state.get("Sort_Multi_Select_Garbage_First", 0) == 0:
            return "sort_multi_select_garbage_first"
        
        # All sorting complete, check Upgrade Characters Level
        if state.get("Upgrade_Characters_Level", 0) == 0:
            return "upgrade_characters_level"
        
        # Upgrade Characters complete, check Recive Giftbox Orbs
        if state.get("Recive_Giftbox_Orbs", 0) == 0:
            return "recive_giftbox_orbs"
        
        # Recive Giftbox Orbs complete, check Main Screenshot
        if state.get("ScreenShot_MainMenu", 0) == 0:
            return "main_screenshot"
        
        # Screenshot complete, check Extract Orb Count
        if state.get("Orbs", "0") in ["0", ""]:
            return "extract_orb_counts"
        
        # Orb extraction complete, check Extract Account ID
        if state.get("AccountID", "") == "":
            return "extract_account_id"
        
        # Account ID extraction complete, check account linking status
        if state.get("isLinked", 0) != 1:
            # Not linked yet - check Login1 Prepare for Link
            if state.get("Login1_Prepare_Link", 0) == 0:
                return "login1_prepare_for_link"
        
        # Login preparation complete, proceed to Kon Bonaza (for non-linked accounts)
        if state.get("Skip_Kon_Bonaza_100Times", 0) < 100:
            return "skip_kon_bonaza"
        
        # If account is linked and all tasks are done, just stay in main (waiting state)
        # The automatic account fetcher will handle the next cycle
        if state.get("isLinked", 0) == 1:
            return "main"  # Stay in main, waiting for new accounts
        
        # Everything complete but not linked yet
        return "main"  # Default fallback
    
    def should_skip_to_mode(self, device_id: str) -> str:
        """Determine if device should skip to a specific mode after restarting"""
        return self.get_next_task_set_after_restarting(device_id)
    
    def update_session_stats(self, device_id: str, task_name: str):
        """Update session statistics"""
        with self.locks.get(device_id, Lock()):
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            if "SessionStats" not in self.states[device_id]:
                self.states[device_id]["SessionStats"] = {
                    "SessionStartTime": self._get_istanbul_time(),
                    "TasksExecuted": 0,
                    "LastTaskExecuted": None
                }
            
            self.states[device_id]["SessionStats"]["TasksExecuted"] += 1
            self.states[device_id]["SessionStats"]["LastTaskExecuted"] = task_name
            self._save_state(device_id)
    
    def get_progress_summary(self, device_id: str) -> str:
        """Get a summary of device progress"""
        state = self.get_state(device_id)
        device_name = self._get_device_name(device_id)
        
        # Build progress indicators
        modes = []
        if state.get("EasyMode", 0) == 1:
            modes.append("Easy✓")
        if state.get("HardMode", 0) == 1:
            modes.append("Hard✓")
        if state.get("SideMode", 0) == 1:
            modes.append("Side✓")
        if state.get("SubStory", 0) == 1:
            modes.append("Sub✓")
        if state.get("Character_Slots_Purchased", 0) == 1:
            modes.append("Slots✓")
        if state.get("Recive_GiftBox", 0) == 1:
            modes.append("Gift✓")
        if state.get("Skip_Yukio_Event", 0) == 1:
            modes.append("Yukio✓")
        if state.get("Recive_Giftbox_Orbs", 0) == 1:
            modes.append("GiftOrbs✓")
        
        kon_bonaza = state.get("Skip_Kon_Bonaza_100Times", 0)
        if kon_bonaza > 0:
            modes.append(f"Kon:{kon_bonaza}/100")
        
        if not modes:
            modes.append("Starting")
        
        restart_count = state.get("RestartingCount", 0)
        linked = "Linked" if state.get("isLinked", 1) == 1 else "Unlinked"
        
        # Account info
        account_id = state.get("AccountID", "")
        account_str = f" ID:{account_id[:8]}..." if account_id else ""
        
        return f"{device_name}: [{' → '.join(modes)}] ({linked}) Restarts:{restart_count}{account_str}"
    
    def print_all_device_states(self):
        """Print a summary of all device states"""
        print("\n" + "="*70)
        print("DEVICE STATE SUMMARY")
        print("="*70)
        
        for device_id in sorted(self.device_mapping.keys()):
            print(self.get_progress_summary(device_id))
        
        print("="*70 + "\n")
    
    def _get_stock_file_path(self) -> str:
        """Get the path for the currentlyStock.json file"""
        return os.path.join(self.state_dir, "currentlyStock.json")
    
    def _initialize_stock_file(self):
        """Initialize the currentlyStock.json file with auto-generation"""
        stock_file = self._get_stock_file_path()
        
        # Check if file exists, if not create it with default values
        if not os.path.exists(stock_file):
            self._create_default_stock_file()
            print("[STOCK] Created new currentlyStock.json file")
        else:
            # Verify file integrity and add missing keys if needed
            try:
                with open(stock_file, 'r') as f:
                    stock_data = json.load(f)
                
                # Ensure STOCK key exists
                if "STOCK" not in stock_data:
                    stock_data["STOCK"] = 1
                    self._save_stock_data(stock_data)
                    print("[STOCK] Added missing STOCK key to currentlyStock.json")
                    
            except (json.JSONDecodeError, Exception) as e:
                print(f"[STOCK] Error reading stock file, recreating: {e}")
                self._create_default_stock_file()
    
    def _create_default_stock_file(self):
        """Create the default currentlyStock.json file"""
        default_stock = {
            "STOCK": 1,
            "LastUpdated": self._get_istanbul_time()
        }
        self._save_stock_data(default_stock)
    
    def _save_stock_data(self, stock_data: Dict[str, Any]):
        """Save stock data to currentlyStock.json"""
        stock_file = self._get_stock_file_path()
        try:
            stock_data["LastUpdated"] = self._get_istanbul_time()
            with open(stock_file, 'w') as f:
                json.dump(stock_data, f, indent=2)
        except Exception as e:
            print(f"[STOCK] Error saving stock file: {e}")
    
    def _load_stock_data(self) -> Dict[str, Any]:
        """Load stock data from currentlyStock.json with auto-generation"""
        stock_file = self._get_stock_file_path()
        
        # Auto-generate if file doesn't exist
        if not os.path.exists(stock_file):
            print("[STOCK] File missing, auto-generating currentlyStock.json")
            self._create_default_stock_file()
        
        try:
            with open(stock_file, 'r') as f:
                stock_data = json.load(f)
            
            # Ensure STOCK key exists
            if "STOCK" not in stock_data:
                stock_data["STOCK"] = 1
                self._save_stock_data(stock_data)
                print("[STOCK] Auto-added missing STOCK key")
                
            return stock_data
        except (json.JSONDecodeError, Exception) as e:
            print(f"[STOCK] Error loading stock file, recreating: {e}")
            self._create_default_stock_file()
            return {"STOCK": 1, "LastUpdated": self._get_istanbul_time()}
    
    def get_current_stock(self) -> int:
        """Get current stock value"""
        stock_data = self._load_stock_data()
        return stock_data.get("STOCK", 1)
    
    def increment_stock(self, device_id: str = None) -> int:
        """Increment stock value by 1 and return new value"""
        stock_data = self._load_stock_data()
        current_stock = stock_data.get("STOCK", 1)
        new_stock = current_stock + 1
        stock_data["STOCK"] = new_stock
        self._save_stock_data(stock_data)
        
        # Log the increment with device info if provided
        if device_id:
            device_name = self._get_device_name(device_id)
            print(f"[{device_name}] Stock incremented: {current_stock} → {new_stock}")
        else:
            print(f"[STOCK] Stock incremented: {current_stock} → {new_stock}")
        
        return new_stock
    
    def set_stock(self, value: int, device_id: str = None) -> int:
        """Set stock to a specific value"""
        stock_data = self._load_stock_data()
        old_stock = stock_data.get("STOCK", 1)
        stock_data["STOCK"] = value
        self._save_stock_data(stock_data)
        
        # Log the change with device info if provided
        if device_id:
            device_name = self._get_device_name(device_id)
            print(f"[{device_name}] Stock set: {old_stock} → {value}")
        else:
            print(f"[STOCK] Stock set: {old_stock} → {value}")
        
        return value

# Global instance
device_state_manager = DeviceStateManager()