# tasks/restarting_tasks.py - Complete tasks for game startup and initial navigation

Restarting_Tasks = [
        # From Restarting_Tasks to Main_Tasks
        {
        "task_name": "Open Story Window",
        "type": "pixel",
        "click_location_str": "531,193",
        "search_array": ["479,146","#ebebea","457,184","#ffffff","524,191","#ffffff"],
        "isLogical": False,
        "BackToStory": True,  # Switches to Main_Tasks,
        "StopSupport": "json_SideMode"
    },
        {
        "task_name": "Click [Sub-Stories] Window.",
        "type": "pixel",
        "click_location_str": "694,189",
        "search_array": ["679,180","#ffffff","736,202","#ffffff","794,201","#9c1212","791,204","#9c1212"],
        "priority": 1,
        "cooldown": 5.0,
        "ConditionalRun": ["EasyMode", "HardMode", "SideMode"],  # Dynamic conditional checking
        "Sub-Stores": True,  # Switch to sub-stories if conditions are met
    },
    # HIGHEST PRIORITY - Error Recovery/Back Navigation (Priority 5-10)
    {
        "task_name": "Click[Back] In Selling Character Window",
        "type": "pixel",
        "click_location_str": "23,22",
        "search_array": ["216,512","#e24601","74,26","#ffffff","24,21","#ffffff","53,27","#ffffff"],
        "isLogical": False,
        "priority": 5,
        "cooldown": 2.0,
    },
    
    # HIGH PRIORITY - Game Start/Mod Menu (Priority 10-15)
    {
        "task_name": "Click [Thank You] For Mod Menu",
        "type": "pixel",
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 3.0,
    },
    {
        "task_name": "Click [Game Start]",
        "type": "pixel",
        "click_location_str": "477,452",
        "search_array": ["880,490","#515151","937,512","#e60012"],
        "isLogical": False,
        "priority": 15,
        "cooldown": 3.0,
    },
    {
        "task_name": "Click [Game Start 2]",
        "type": "pixel",
        "click_location_str": "471,450",
        "search_array": ["845,505","#fdfdfd","856,513","#e81828","14,21","#ffffff"],
        "isLogical": False,
        "priority": 15,
        "cooldown": 3.0,
    },
    
    # MEDIUM PRIORITY - Quest/Event Handling (Priority 20-30)
    {
        "task_name": "Click [Yes] For Paused Quest Error",
        "type":"pixel",
        "click_location_str": "619,373",
        "search_array": ["251,153","#0d12b5","260,165","#e60012","432,151","#191925","239,224","#ffffff","368,227","#ffffff"],
        "isLogical": False,
        "priority": 20,
        "cooldown": 2.0,
    },
       {
        "task_name": "Click [Yes] For Continue Playing Quest",
        "type":"pixel",
        "click_location_str": "621,373",
        "search_array": ["246,154","#0d12b5","262,164","#e60012","430,276","#ffffff","471,275","#ffffff","496,275","#ffffff"],
        "isLogical": False,
        "priority": 20,
        "cooldown": 2.0,
    },
    {
        "task_name": "Exit News",
        "type": "template",
        "template_path": "templates/Restarting/Exit.png",
        "roi": [731, 0, 228, 133],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "shared_detection": True,
        "priority": 25,
        "cooldown": 2.0,
    },
    
    # LOWER PRIORITY - Navigation/Menu Access (Priority 35-40)
    {
        "task_name": "Open [SOLO] Menu",
        "type": "template",
        "template_path": "templates/Restarting/Solo.png",
        "roi": [814, 420, 142, 118],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "priority": 35,
        "cooldown": 2.0,
    },
    
    # LOW PRIORITY - Login Bonuses (Priority 40-50)
    {
        "task_name": "Login Bonus Begginer",
        "type": "pixel",
        "click_location_str": "534,338",
        "search_array": ["195,93","#e50012","182,82","#0d12b4","334,79","#191925"],
        "isLogical": False,
        "priority": 40,
        "cooldown": 3.0,
    },
    {
        "task_name": "Login Bonus",
        "type": "pixel",
        "click_location_str": "626,510",
        "search_array": ["405,36","#191925","483,36","#191925","255,47","#e50012","255,35","#0d12b4"],
        "isLogical": False,
        "priority": 40,
        "cooldown": 3.0,
    },
    {
        "task_name": "Skip Any New Events/Windows Opened By Clicking [OK]",
        "type": "template",
        "template_path": "templates/Restarting/OK.png",
        "roi": [2, 285, 559, 244],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "shared_detection": True,  # Check with other UI elements
        "priority": 50,
        "cooldown": 2.0,
    },
]