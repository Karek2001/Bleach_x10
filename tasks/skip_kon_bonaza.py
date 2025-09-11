# tasks/skip_kon_bonaza.py - Tasks for skipping Kon Bonanza 100 times

Skip_Kon_Bonaza = [
    # Navigate to Kon Bonanza
    {
        "task_name": "Open Kon Bonanza Menu",
        "type": "template",
        "template_path": "templates/Kon_Bonaza/Kon_Bonaza_Icon.png",
        "roi": [100, 300, 200, 200],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
    },
    
    # Start Kon Bonanza
    {
        "task_name": "Start Kon Bonanza",
        "type": "template",
        "template_path": "templates/Kon_Bonaza/Start_Bonaza.png",
        "roi": [350, 400, 260, 80],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "priority": 15,
        "cooldown": 3.0,
    },
    
    # Skip the Kon Bonanza animation
    {
        "task_name": "Skip Kon Bonanza Animation",
        "type": "template",
        "template_path": "templates/Kon_Bonaza/Skip_Animation.png",
        "roi": [830, 1, 129, 59],
        "confidence": 0.85,
        "use_match_position": True,
        "isLogical": False,
        "priority": 20,
        "cooldown": 2.0,
        "Increment_Kon_Bonaza": True,  # Increment the counter
    },
    
    # Collect rewards
    {
        "task_name": "Collect Kon Bonanza Rewards",
        "type": "pixel",
        "click_location_str": "480,450",
        "search_array": ["480,450","#00ff00","400,450","#00ff00","560,450","#00ff00"],
        "isLogical": False,
        "priority": 25,
        "cooldown": 3.0,
    },
    
    # Check if reached 100 skips
    {
        "task_name": "Check Kon Bonaza Complete",
        "type": "ConditionalCheck",
        "check_key": "Skip_Kon_Bonaza_100Times",
        "check_value": 100,
        "check_operator": ">=",
        "ScreenShot_MainMenu_Tasks": True,  # Move to screenshot task
        "priority": 30,
        "cooldown": 5.0,
    },
    
    # Continue if not complete
    {
        "task_name": "Continue Kon Bonanza",
        "type": "pixel",
        "click_location_str": "480,480",
        "search_array": ["480,480","#ffffff","400,480","#ffffff","560,480","#ffffff"],
        "isLogical": False,
        "priority": 35,
        "cooldown": 3.0,
        "StopSupport": "json_Skip_Kon_Bonaza_Complete",  # Stop if already complete
    },
    
    # Exit if daily limit reached
    {
        "task_name": "Exit Kon Bonanza - Daily Limit",
        "type": "pixel",
        "click_location_str": "25,25",
        "search_array": ["480,250","#ff0000","480,260","#ffffff"],
        "isLogical": False,
        "BackToRestartingTasks": True,
        "priority": 40,
        "cooldown": 5.0,
    },
]