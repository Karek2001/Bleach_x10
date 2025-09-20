Tutorial: Adding Tasks to the Automation System
Part 1: Adding a Main Task with Device State Tracking
Overview
Main tasks are tasks that track progress in the device's JSON state file and are part of the sequential task progression system.



Step-by-Step Guide
Step 1: Define Your Task Array
Create a new file in the tasks/ folder, e.g., tasks/your_new_task.py:
```
Your_New_Task = [
    {
        "task_name": "Click [Your Button Name]",
        "type": "pixel",  # or "template"
        "click_location_str": "480,350",
        "search_array": ["100,200","#ffffff","150,200","#000000"],
        "priority": 10,
        "cooldown": 5.0,
        "json_YourTaskName": True,  # This sets the completion flag
        "NextTaskSet_Tasks": True   # This triggers the next task set
    }
]
```

Step 2: Add State Tracking to device_state_manager.py
In device_state_manager.py, add your new state key in _get_default_state():
```
def _get_default_state(self) -> Dict[str, Any]:
    return {
        # ... existing keys ...
        "YourTaskName": 0,  # Add your new state key here
        # ... rest of the keys ...
    }
```
Add flag mapping in set_json_flag() method:
```
flag_mapping = {
    # ... existing mappings ...
    "json_YourTaskName": "YourTaskName",  # Add your mapping
}
```
Add to check_stop_support() if you want tasks to be skipped after completion:
```
flag_mapping = {
    # ... existing mappings ...
    "json_YourTaskName": "YourTaskName",  # For StopSupport checking
}
```

Step 3: Add Task Set to background_process.py
In background_process.py, update the ProcessMonitor class:
```
# In get_active_tasks() method, add to task_map:
task_map = {
    # ... existing mappings ...
    "your_task_set": Your_New_Task,
}

# In set_active_tasks() method, add to valid_sets:
valid_sets = [
    # ... existing sets ...
    "your_task_set",
]

# In handle_task_flags(), add your flag handler:
flag_handlers = {
    # ... existing handlers ...
    "YourTaskSet_Tasks": ("your_task_set", "→ Your Task Set"),
}
```

Step 4: Update Task Progression Logic
In device_state_manager.py, update get_next_task_set_after_restarting():
```
def get_next_task_set_after_restarting(self, device_id: str) -> str:
    state = self.get_state(device_id)
    
    # ... existing checks ...
    
    # Add your task check in the appropriate position
    if state.get("YourTaskName", 0) == 0:
        return "your_task_set"
    
    # ... rest of the checks ...
```

Step 5: Import Your Task
In tasks/__init__.py, add:

```
from .your_new_task import Your_New_Task

__all__ = [
    # ... existing exports ...
    'Your_New_Task'
]
```

