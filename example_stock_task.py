#!/usr/bin/env python3
"""
Example task configuration showing how to use the increment_stock flag.
This file demonstrates how to create tasks that increment the stock value.
"""

# Example tasks that use the increment_stock flag
example_stock_tasks = [
    {
        "task_name": "Collect Reward and Increment Stock",
        "type": "pixel", 
        "search_array": ["100,200", "#FF5733", "150,250", "#33FF57"],
        "click_location_str": "125,225",
        "cooldown": 3.0,
        "priority": 10,
        # This flag will increment the stock by 1 when the task is executed
        "increment_stock": True,
        "description": "Collect reward button - increments stock counter"
    },
    
    {
        "task_name": "Complete Mission with Stock Tracking",
        "type": "template",
        "template_path": "templates/complete_mission.png", 
        "threshold": 0.8,
        "click_location_str": "400,300",
        "cooldown": 5.0,
        "priority": 15,
        # This will also increment stock when executed
        "increment_stock": True,
        "description": "Complete mission button - tracks completion in stock"
    },
    
    {
        "task_name": "OCR Stock Item Detection",
        "type": "ocr",
        "ocr_text": "item collected,reward received",
        "roi": [100, 150, 200, 50],
        "cooldown": 2.0,
        "priority": 20,
        # Increment stock when OCR detects the text
        "increment_stock": True,
        "description": "Detects item collection text and increments stock"
    },
    
    {
        "task_name": "Conditional Stock Increment",
        "type": "pixel",
        "search_array": ["300,400", "#123456"],
        "click_location_str": "300,400",
        "cooldown": 1.0,
        "priority": 25,
        # Only increment stock if certain conditions are met
        "increment_stock": True,
        # Example: Only run this task if EasyMode is not complete
        "StopSupport": "json_EasyMode",
        "description": "Conditional stock increment - only when EasyMode incomplete"
    }
]

# How to use in your task files:
"""
To use the increment_stock functionality in your tasks:

1. Add "increment_stock": True to any task dictionary
2. When the task matches and executes, the stock will automatically increment by 1
3. The currentlyStock.json file will be updated with the new value
4. If the file gets deleted, it will auto-regenerate with STOCK: 1

Example usage in a task list:
my_task = {
    "task_name": "My Custom Task",
    "type": "pixel",
    "search_array": ["x,y", "#hexcolor"],
    "click_location_str": "x,y", 
    "increment_stock": True  # <- Add this line
}

The stock value can be checked anytime by:
- Reading device_states/currentlyStock.json
- Using device_state_manager.get_current_stock()
- The stock increments globally across all devices
"""

if __name__ == "__main__":
    print("Example Stock Tasks Configuration")
    print("="*50)
    
    for i, task in enumerate(example_stock_tasks, 1):
        print(f"\nTask {i}: {task['task_name']}")
        print(f"  Type: {task['type']}")
        print(f"  Increment Stock: {task.get('increment_stock', False)}")
        print(f"  Description: {task.get('description', 'No description')}")
    
    print(f"\nTotal example tasks: {len(example_stock_tasks)}")
    print("\nTo use these tasks, add them to your task lists in the tasks/ directory.")
