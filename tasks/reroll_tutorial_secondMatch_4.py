# reroll_tutorial_secondMatch_4.py - Second tutorial match
reroll_tutorial_secondmatch_tasks = [
       {
        "task_name": "Click [Thank You] For Mod Menu [Reroll Second Match]",
        "type": "pixel", 
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Start Second Tutorial Battle",
        "type": "pixel",
        "click_location_str": "480,450",
        "search_array": ["450,430","#4caf50","510,430","#4caf50","480,450","#ffffff"],
        
        "priority": 1,
        "cooldown": 2.0
    },
    {
        "task_name": "Tutorial Battle Instructions",
        "type": "pixel",
        "click_location_str": "800,50",
        "search_array": ["780,30","#ffffff","820,30","#ffffff","800,50","#424242"],
        
        "priority": 2,
        "cooldown": 1.0
    },
    {
        "task_name": "Attack Enemy Tutorial",
        "type": "pixel",
        "click_location_str": "480,350",
        "search_array": ["460,330","#f44336","500,330","#f44336","480,350","#212121"],
        
        "priority": 3,
        "cooldown": 0.5,
        "repeat": 8  # More attacks for second battle
    },
    {
        "task_name": "Use Strong Attack",
        "type": "pixel",
        "click_location_str": "650,450",
        "search_array": ["630,430","#9c27b0","670,430","#9c27b0","650,450","#ffffff"],
        
        "priority": 4,
        "cooldown": 1.5
    },
    {
        "task_name": "Use Special Move Again",
        "type": "pixel",
        "click_location_str": "800,450",
        "search_array": ["780,430","#ffeb3b","820,430","#ffeb3b","800,450","#ffffff"],
        
        "priority": 5,
        "cooldown": 3.0
    },
    {
        "task_name": "Second Victory Screen",
        "type": "pixel",
        "click_location_str": "480,500",
        "search_array": ["450,480","#ffc107","510,480","#ffc107","480,500","#ffffff"],
        
        "priority": 6,
        "cooldown": 2.0,
        "json_Reroll_Tutorial_SecondMatch": True,  # Mark this reroll task as complete
        "Reroll_ReplaceIchigoWithFiveStar_Tasks": True  # Switch to replace Ichigo task
    },
    {
        "task_name": "Collect Battle Rewards",
        "type": "pixel",
        "click_location_str": "480,520",
        "search_array": ["450,500","#4caf50","510,500","#4caf50","480,520","#ffffff"],
        
        "priority": 7,
        "cooldown": 2.0,
        "json_Reroll_Tutorial_SecondMatch": True,  # Mark this reroll task as complete
        "Reroll_ReplaceIchigoWithFiveStar_Tasks": True  # Switch to replace Ichigo task
    }
]
