# main_screenshot_tasks.py - Main Menu Screenshot Tasks
"""
Main screenshot tasks that capture screenshots of the main menu
for account management and tracking purposes.
"""

Main_Screenshot_Tasks = [
    {
        "task_name": "Take Main Menu Screenshot",
        "type": "pixel",
        "click_location_str": "0,0",  # No click, just detection
        "search_array": ["899,485","#978e74","388,480","#e1773a","790,16","#593b0d",],  # Simple detection of screen center
        "priority": 5,
        "cooldown": 1.0,
        "save_screenshot_with_username": True,
        "json_ScreenShot_MainMenu": True,
        "Extract_Orb_Count_Tasks": True
    }
]
