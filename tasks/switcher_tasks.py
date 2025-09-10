# tasks/switcher_tasks.py - Tasks responsible for switching between task sets

Switcher_Tasks = [
        # STORY COMPLETED LET'S Back To Restarting SO WE CAN RESTART THE GAME
    {
        "task_name": "Story Completed",
        "type": "pixel",
        "click_location_str": "482,373",
        "search_array": ["395,155","#191925","460,152","#191925","567,155","#191925","263,154","536,153","#191925","#0d12b5","265,166","#e60012"],
        "isLogical": False,
        "shared_detection": True,
        "priority": 1,
        "cooldown": 5.0,
        "BackToRestarting": True,
    },
    # From Restarting_Tasks to GUILD_TUTORIAL_TASKS
    {
        "task_name": "Guild Tutorial Detected",
        "type": "template",
        "template_path": "templates/Switcher/ArrowShowedUP.png",
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
        "search_array": ["718,148","#0d12b5","709,163","#e60012","418,372","#ffffff","513,372","#ffffff"],
        "isLogical": False,
        "Characters_Full": True,  # Switches to Sell_Characters
    },
        {
        "task_name": "Character FULL #2",
        "type": "pixel",
        "click_location_str": "0,0",  # No click needed, just detection
        "search_array": ["257,154","#0d12b5","262,164","#e60012","491,236","#ffffff","591,237","#ffffff"],
        "isLogical": False,
        "Characters_Full": True,  # Switches to Sell_Characters
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
        # We Need to Sell Accsesurry
    {
        "task_name": "Detected Sell Accessury",
        "type": "pixel",
        "click_location_str": "486,375",
        "search_array": ["708,149","#0d12b5","708,161","#e60012","587,269","#ffffff","700,274","#ffffff","584,296","#ffffff"],
        "isLogical": False,
        "SellAccsesurry": True,
    },


    
]