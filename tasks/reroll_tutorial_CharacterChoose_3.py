# reroll_tutorial_CharacterChoose_3.py - Character selection in tutorial
reroll_tutorial_characterchoose_tasks = [
   {
        "task_name": "Click [Thank You] For Mod Menu [Reroll Character Choose]",
        "type": "pixel",
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Open Character Select",
        "type": "pixel",
        "click_location_str": "480,400",
        "search_array": ["450,380","#9c27b0","510,380","#9c27b0","480,400","#ffffff"],
        "isLogical": False,
        "priority": 1,
        "cooldown": 2.0
    },
    {
        "task_name": "Select Ichigo",
        "type": "pixel",
        "click_location_str": "300,300",
        "search_array": ["280,280","#ff6f00","320,280","#ff6f00","300,300","#ffffff"],
        "isLogical": False,
        "priority": 2,
        "cooldown": 1.5
    },
    {
        "task_name": "Confirm Character Selection",
        "type": "pixel",
        "click_location_str": "600,500",
        "search_array": ["580,480","#4caf50","620,480","#4caf50","600,500","#ffffff"],
        "isLogical": False,
        "priority": 3,
        "cooldown": 2.0
    },
    {
        "task_name": "Tutorial Team Setup",
        "type": "pixel",
        "click_location_str": "480,450",
        "search_array": ["450,430","#2196f3","510,430","#2196f3","480,450","#ffffff"],
        "isLogical": False,
        "priority": 4,
        "cooldown": 2.0
    },
    {
        "task_name": "Confirm Team",
        "type": "pixel",
        "click_location_str": "700,500",
        "search_array": ["680,480","#4caf50","720,480","#4caf50","700,500","#ffffff"],
        "isLogical": False,
        "priority": 5,
        "cooldown": 2.0,
        "json_Reroll_Tutorial_CharacterChoose": True,
        "Reroll_Tutorial_SecondMatch_Tasks": True  # Switch to second match
    },
    {
        "task_name": "Tutorial Continue",
        "type": "pixel",
        "click_location_str": "480,520",
        "search_array": ["450,500","#ff9800","510,500","#ff9800","480,520","#ffffff"],
        "isLogical": False,
        "priority": 6,
        "cooldown": 1.0,
        "json_Reroll_Tutorial_CharacterChoose": True,
        "Reroll_Tutorial_SecondMatch_Tasks": True
    }
]
