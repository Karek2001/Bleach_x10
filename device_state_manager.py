# device_state_manager.py - Enhanced with SubStory tracking and JSON flag support
import json
import os
from typing import Dict, Any
from datetime import datetime
import asyncio
from threading import Lock

class DeviceStateManager:
    """Manages persistent state for each device including character upgrades and substory progress"""
    
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
        
        # Create state directory if it doesn't exist
        os.makedirs(self.state_dir, exist_ok=True)
        
        # Initialize states for all devices
        self._initialize_all_devices()
    
    def _get_device_name(self, device_id: str) -> str:
        """Get device name from device ID"""
        return self.device_mapping.get(device_id, f"DEVICE_{device_id.replace(':', '_')}")
    
    def _get_state_file_path(self, device_name: str) -> str:
        """Get the JSON file path for a device"""
        return os.path.join(self.state_dir, f"{device_name}.json")
    
    def _get_default_state(self) -> Dict[str, Any]:
        """Get default state structure for a new device"""
        return {
            "EasyMode": 0,
            "HardMode": 0,
            "SideMode": 0,
            "SubStory": 0,  # Main SubStory flag
            "SubStory-TheHumanWorld": 0,
            "SubStory-TheSoulSociety": 0,
            "SubStory-HuecoMundo": 0,
            "SubStory-TheFutureSociety": 0,
            "SubStory-Others": 0,
            "RestartingCount": 0,
            "2-Stars-Upgraded": 0,
            "3-Stars-Upgraded": 0,
            "4-Stars-Upgraded": 0,
            "5-Stars-Upgraded": 0,
            "isLinked": False,
            "LastUpdated": datetime.now().isoformat(),
            "CurrentTaskSet": "restarting",
            "SessionStats": {
                "SessionStartTime": datetime.now().isoformat(),
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
                        
                    # Ensure all required keys exist (for backward compatibility)
                    default_state = self._get_default_state()
                    for key, value in default_state.items():
                        if key not in loaded_state:
                            loaded_state[key] = value
                    
                    self.states[device_id] = loaded_state
                    print(f"[STATE] Loaded existing state for {device_name}")
                except Exception as e:
                    print(f"[STATE] Error loading state for {device_name}: {e}")
                    self.states[device_id] = self._get_default_state()
                    self._save_state(device_id)
            else:
                self.states[device_id] = self._get_default_state()
                self._save_state(device_id)
                print(f"[STATE] Created new state file for {device_name}")
    
    def _save_state(self, device_id: str):
        """Save device state to JSON file"""
        device_name = self._get_device_name(device_id)
        state_file = self._get_state_file_path(device_name)
        
        try:
            self.states[device_id]["LastUpdated"] = datetime.now().isoformat()
            with open(state_file, 'w') as f:
                json.dump(self.states[device_id], f, indent=2)
        except Exception as e:
            print(f"[STATE] Error saving state for {device_name}: {e}")
    
    def get_state(self, device_id: str) -> Dict[str, Any]:
        """Get current state for a device"""
        if device_id not in self.states:
            self.states[device_id] = self._get_default_state()
        return self.states[device_id].copy()
    
    def update_state(self, device_id: str, key: str, value: Any):
        """Update a specific state value for a device"""
        with self.locks.get(device_id, Lock()):
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            self.states[device_id][key] = value
            
            # Check if all SubStory sub-keys are complete
            self._check_substory_completion(device_id)
            
            self._save_state(device_id)
    
    def _check_substory_completion(self, device_id: str):
        """Check if all SubStory sub-keys are complete and update main SubStory flag"""
        substory_keys = [
            "SubStory-TheHumanWorld",
            "SubStory-TheSoulSociety",
            "SubStory-HuecoMundo",
            "SubStory-TheFutureSociety",
            "SubStory-Others"
        ]
        
        # Check if all substory keys are set to 1 (true)
        all_complete = all(
            self.states[device_id].get(key, 0) == 1 
            for key in substory_keys
        )
        
        if all_complete:
            self.states[device_id]["SubStory"] = 1
            print(f"[{self._get_device_name(device_id)}] ✓ All SubStories complete!")
    
    def set_json_flag(self, device_id: str, flag_name: str, value: Any = 1):
        """Set a JSON flag based on task detection"""
        # Map json_ prefixed flags to actual state keys
        flag_mapping = {
            "json_EasyMode": "EasyMode",
            "json_HardMode": "HardMode",
            "json_SideMode": "SideMode",
            "json_SubStory": "SubStory",
            "json_S_TheHumanWorld": "SubStory-TheHumanWorld",
            "json_S_TheSoulSociety": "SubStory-TheSoulSociety",
            "json_S_HuecoMundo": "SubStory-HuecoMundo",
            "json_S_TheFutureSociety": "SubStory-TheFutureSociety",
            "json_S_Others": "SubStory-Others"
        }
        
        if flag_name in flag_mapping:
            state_key = flag_mapping[flag_name]
            self.update_state(device_id, state_key, value)
            device_name = self._get_device_name(device_id)
            print(f"[{device_name}] Set {state_key} = {value}")
    
    def check_stop_support(self, device_id: str, stop_flag: str) -> bool:
        """Check if a task should be stopped based on device state"""
        # Map json_ prefixed flags to actual state keys
        flag_mapping = {
            "json_EasyMode": "EasyMode",
            "json_HardMode": "HardMode",
            "json_SideMode": "SideMode",
            "json_SubStory": "SubStory",
            "json_S_TheHumanWorld": "SubStory-TheHumanWorld",
            "json_S_TheSoulSociety": "SubStory-TheSoulSociety",
            "json_S_HuecoMundo": "SubStory-HuecoMundo",
            "json_S_TheFutureSociety": "SubStory-TheFutureSociety",
            "json_S_Others": "SubStory-Others"
        }
        
        if stop_flag in flag_mapping:
            state_key = flag_mapping[stop_flag]
            state = self.get_state(device_id)
            return state.get(state_key, 0) == 1
        
        return False
    
    def increment_counter(self, device_id: str, counter_name: str):
        """Increment a counter value"""
        with self.locks.get(device_id, Lock()):
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            current_value = self.states[device_id].get(counter_name, 0)
            self.states[device_id][counter_name] = current_value + 1
            self._save_state(device_id)
    
    def increment_star_upgrade(self, device_id: str, star_level: int):
        """Increment character upgrade counter for specific star level"""
        counter_name = f"{star_level}-Stars-Upgraded"
        if counter_name in ["2-Stars-Upgraded", "3-Stars-Upgraded", "4-Stars-Upgraded", "5-Stars-Upgraded"]:
            self.increment_counter(device_id, counter_name)
            device_name = self._get_device_name(device_id)
            print(f"[{device_name}] {counter_name}: {self.states[device_id][counter_name]}")
    
    def set_linked_status(self, device_id: str, is_linked: bool):
        """Set the linked status of a device account"""
        self.update_state(device_id, "isLinked", is_linked)
        device_name = self._get_device_name(device_id)
        status = "linked" if is_linked else "not linked"
        print(f"[{device_name}] Account {status}")
    
    def mark_easy_mode_complete(self, device_id: str):
        """Mark EasyMode as complete for a device"""
        self.update_state(device_id, "EasyMode", 1)
    
    def mark_hard_mode_complete(self, device_id: str):
        """Mark HardMode as complete (and EasyMode if not already)"""
        with self.locks.get(device_id, Lock()):
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            # If HardMode is complete, EasyMode must also be complete
            self.states[device_id]["EasyMode"] = 1
            self.states[device_id]["HardMode"] = 1
            self._save_state(device_id)
    
    def mark_side_mode_active(self, device_id: str):
        """Mark that SideMode is active (EasyMode and HardMode must be complete)"""
        with self.locks.get(device_id, Lock()):
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            # If SideMode is active, both Easy and Hard must be complete
            self.states[device_id]["EasyMode"] = 1
            self.states[device_id]["HardMode"] = 1
            self.states[device_id]["SideMode"] = 1
            self._save_state(device_id)
    
    def get_recommended_task_set(self, device_id: str) -> str:
        """Get the recommended task set based on device state"""
        state = self.get_state(device_id)
        
        if state.get("SubStory", 0) == 1:
            return "substory"
        
        if state.get("SideMode", 0) == 1:
            return "sidestory"
        
        if state.get("HardMode", 0) == 1:
            return "sidestory"
        
        if state.get("EasyMode", 0) == 1:
            return "hardstory"
        
        return "main"
    
    def should_skip_to_mode(self, device_id: str) -> str:
        """Determine if device should skip to a specific mode after restarting"""
        state = self.get_state(device_id)
        
        if state.get("SubStory", 0) == 1:
            return "substory"
        elif state.get("SideMode", 0) == 1:
            return "sidestory"
        elif state.get("HardMode", 0) == 1:
            return "sidestory"
        elif state.get("EasyMode", 0) == 1:
            return "hardstory"
        
        return "main"
    
    def update_session_stats(self, device_id: str, task_name: str):
        """Update session statistics"""
        with self.locks.get(device_id, Lock()):
            if device_id not in self.states:
                self.states[device_id] = self._get_default_state()
            
            if "SessionStats" not in self.states[device_id]:
                self.states[device_id]["SessionStats"] = {
                    "SessionStartTime": datetime.now().isoformat(),
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
        
        modes = []
        if state.get("EasyMode", 0) == 1:
            modes.append("Easy✓")
        if state.get("HardMode", 0) == 1:
            modes.append("Hard✓")
        if state.get("SideMode", 0) == 1:
            modes.append("Side✓")
        if state.get("SubStory", 0) == 1:
            modes.append("Sub✓")
        
        # Check individual substories
        substories = []
        if state.get("SubStory-TheHumanWorld", 0) == 1:
            substories.append("HW")
        if state.get("SubStory-TheSoulSociety", 0) == 1:
            substories.append("SS")
        if state.get("SubStory-HuecoMundo", 0) == 1:
            substories.append("HM")
        if state.get("SubStory-TheFutureSociety", 0) == 1:
            substories.append("FS")
        if state.get("SubStory-Others", 0) == 1:
            substories.append("O")
        
        if not modes:
            modes.append("Starting")
        
        restart_count = state.get("RestartingCount", 0)
        linked = "Linked" if state.get("isLinked", False) else "Unlinked"
        
        # Character upgrades summary
        upgrades = []
        for stars in [2, 3, 4, 5]:
            count = state.get(f"{stars}-Stars-Upgraded", 0)
            if count > 0:
                upgrades.append(f"{stars}★:{count}")
        
        upgrade_str = f" Upgrades[{', '.join(upgrades)}]" if upgrades else ""
        substory_str = f" Sub[{','.join(substories)}]" if substories else ""
        
        return f"{device_name}: [{' → '.join(modes)}] ({linked}) Restarts:{restart_count}{substory_str}{upgrade_str}"
    
    def print_all_device_states(self):
        """Print a summary of all device states"""
        print("\n" + "="*70)
        print("DEVICE STATE SUMMARY")
        print("="*70)
        
        for device_id in sorted(self.device_mapping.keys()):
            print(self.get_progress_summary(device_id))
        
        print("="*70 + "\n")

# Global instance
device_state_manager = DeviceStateManager()