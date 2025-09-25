# reroll_tutorial_ReplaceIchigoWithFiveStar_5.py - Replace Ichigo with 5-star character
reroll_replaceichigowithfivestar_tasks = [
       {
        "task_name": "Click [Thank You] For Mod Menu [Reroll Replace Ichigo With FiveStar]",
        "type": "pixel",
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Open Team Menu",
        "type": "pixel",
        "click_location_str": "120,500",
        "search_array": ["100,480","#3f51b5","140,480","#3f51b5","120,500","#ffffff"],
        "isLogical": False,
        "priority": 1,
        "cooldown": 2.0
    },
    {
        "task_name": "Click Edit Team",
        "type": "pixel",
        "click_location_str": "700,200",
        "search_array": ["680,180","#ff9800","720,180","#ff9800","700,200","#ffffff"],
        "isLogical": False,
        "priority": 2,
        "cooldown": 1.5
    },
    {
        "task_name": "Select Ichigo to Replace",
        "type": "pixel",
        "click_location_str": "300,300",
        "search_array": ["280,280","#ff6f00","320,280","#ff6f00","300,300","#ffffff"],
        "isLogical": False,
        "priority": 3,
        "cooldown": 1.0
    },
    {
        "task_name": "Open Character List",
        "type": "pixel",
        "click_location_str": "480,450",
        "search_array": ["450,430","#2196f3","510,430","#2196f3","480,450","#ffffff"],
        "isLogical": False,
        "priority": 4,
        "cooldown": 1.5
    },
    {
        "task_name": "Filter 5-Star Characters",
        "type": "pixel",
        "click_location_str": "850,150",
        "search_array": ["830,130","#ffc107","870,130","#ffc107","850,150","#ffffff"],
        "isLogical": False,
        "priority": 5,
        "cooldown": 1.0
    },
    {
        "task_name": "Select 5-Star Character",
        "type": "pixel",
        "click_location_str": "400,300",
        "search_array": ["380,280","#ffeb3b","420,280","#ffeb3b","400,300","#ffffff"],
        "isLogical": False,
        "priority": 6,
        "cooldown": 1.5
    },
    {
        "task_name": "Confirm Character Replace",
        "type": "pixel",
        "click_location_str": "600,500",
        "search_array": ["580,480","#4caf50","620,480","#4caf50","600,500","#ffffff"],
        "isLogical": False,
        "priority": 7,
        "cooldown": 2.0
    },
    {
        "task_name": "Save Team Changes",
        "type": "pixel",
        "click_location_str": "700,500",
        "search_array": ["680,480","#4caf50","720,480","#4caf50","700,500","#ffffff"],
        "isLogical": False,
        "priority": 8,
        "cooldown": 2.0,
        "json_Reroll_ReplaceIchigoWithFiveStar": True,  # Mark this reroll task as complete
        "BackToRestartingTasks": True  # Go to regular restarting tasks after reroll completion
    },
    {
        "task_name": "Return to Main Menu",
        "type": "pixel",
        "click_location_str": "60,60",
        "search_array": ["40,40","#ffffff","80,40","#ffffff","60,60","#616161"],
        "isLogical": False,
        "priority": 9,
        "cooldown": 2.0,
        "json_Reroll_ReplaceIchigoWithFiveStar": True,  # Mark this reroll task as complete
        "BackToRestartingTasks": True  # Return to normal operation
    }
]
