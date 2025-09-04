# tasks/switcher_tasks.py - Tasks responsible for switching between task sets

Switcher_Tasks = [
    # From Restarting_Tasks to Main_Tasks
    {
        "task_name": "Open Story Window",
        "type": "pixel",
        "click_location_str": "531,193",
        "search_array": ["479,146","#ebebea","457,184","#ffffff","524,191","#ffffff"],
        "isLogical": False,
        "BackToStory": True,  # Switches to Main_Tasks
    },
    
    # From Restarting_Tasks to GUILD_TUTORIAL_TASKS
    {
        "task_name": "Guild Tutorial Detected",
        "type": "template",
        "template_path": "templates/ArrowShowedUP.png",
        "roi": [470, 365, 76, 104],
        "confidence": 0.60,
        "use_match_position": False,
        "isLogical": False,
        "NeedGuildTutorial": True,  # Switches to GUILD_TUTORIAL_TASKS
    },
    
    # From any task set to Sell_Characters when characters are full
    {
        "task_name": "Character FULL",
        "type": "pixel",
        "click_location_str": "0,0",  # No click needed, just detection
        "search_array": ["254,151","#0d12b5","268,162","#e60012","255,252","#ffffff","299,251","#ffffff","356,254","#ffffff","432,149","#191919"],
        "isLogical": False,
        "Characters_Full": True,  # Switches to Sell_Characters
        "ShowsIn": ["main_tasks", "restarting_tasks"],  # Only active in these task sets
    },
    
    # From GUILD_TUTORIAL_TASKS to Guild_Rejoin
    {
        "task_name": "Click [OK] For GUILD limit Reached",
        "type": "pixel",
        "click_location_str": "481,372",
        "search_array": ["240,154","#0d12b5","259,165","#e60012","450,153","#191925","505,156","#191925"],
        "isLogical": False,
        "NeedToRejoin": True,  # Switches to Guild_Rejoin
    },
    
    # From Guild_Rejoin back to GUILD_TUTORIAL_TASKS
    {
        "task_name": "Click [Guild TOP] After Rejoin",
        "type": "template",
        "template_path": "templates/Guild/GuildTOP.png",
        "roi": [321, 337, 312, 59],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "isRefreshed": True,  # Returns to GUILD_TUTORIAL_TASKS
    },
    
    # From GUILD_TUTORIAL_TASKS back to Restarting_Tasks
    {
        "task_name": "Back To Main Menu From Guild",
        "type": "pixel",
        "click_location_str": "31,28",
        "search_array": ["792,494","#e6f6f2","517,501","#eeeef2"],
        "isLogical": False,
        "BackToRestartingTasks": True,  # Switches to Restarting_Tasks
    },
    
    # From Sell_Characters back to Restarting_Tasks
    {
        "task_name": "Characters Are Sold [No More Left]",
        "type": "pixel",
        "click_location_str": "315,490",
        "search_array": ["684,487","#7f0000","457,421","#e64801","461,313","#e64801","473,206","#e94b01"],
        "isLogical": False,
        "BackToRestartingTasks": True,  # Switches to Restarting_Tasks
    },
]