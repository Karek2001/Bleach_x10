Helper tasks are triggered by flags but don't track completion state. They're used for temporary operations like sorting, filtering, or navigation.
Step-by-Step Guide
Step 1: Create Helper Task Array
Create tasks/your_helper_task.py:
```
Your_Helper_Task = [
    {
        "task_name": "Helper: Navigate Back",
        "type": "pixel",
        "click_location_str": "30,30",
        "search_array": ["25,25","#ffffff","35,25","#ffffff"],
        "priority": 1,
        "cooldown": 3.0,
        "BackToMainTask": True  # Flag to return to main task
    },
    {
        "task_name": "Helper: Click Sort",
        "type": "template",
        "template_path": "templates/Helper/sort.png",
        "roi": [700, 30, 100, 50],
        "confidence": 0.90,
        "priority": 5,
        "cooldown": 2.0
    }
]
```

Step 2: Add to Task Mapping (No State Required)
In background_process.py:
```
# Only add to task_map, no state tracking needed:
task_map = {
    # ... existing mappings ...
    "your_helper": Your_Helper_Task,
}

# Add to valid_sets:
valid_sets = [
    # ... existing sets ...
    "your_helper",
]

# Add flag handler to trigger helper:
flag_handlers = {
    # ... existing handlers ...
    "YourHelper_Tasks": ("your_helper", "→ Your Helper"),
    "BackToMainTask": ("main", "→ Main"),  # Return flag
}
```

Step 3: Trigger Helper from Another Task
In any task that needs to trigger the helper:
```
{
    "task_name": "Detected Need for Helper",
    "type": "pixel",
    "click_location_str": "0,0",  # Detection only
    "search_array": ["100,100","#ff0000"],
    "priority": 10,
    "YourHelper_Tasks": True  # Triggers helper task set
}
```


Prompt Template for AI Model
When requesting an AI model to add tasks, use this template:
For Main Tasks (With State Tracking):
