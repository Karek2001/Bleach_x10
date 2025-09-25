# reroll_earse_gamedata_1.py - First reroll task to erase game data
reroll_earse_gamedata_tasks = [
       {
        "task_name": "Click [Thank You] For Mod Menu [Reroll Earse GameData]",
        "type": "pixel",
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Click [Menu] [Reroll Earse GameData]",
        "type": "pixel",
        "click_location_str": "858,505",
        "search_array": ["839,505","#ffffff","835,512","#e60012","871,504","#ffffff","940,504","#454c55"],
        "isLogical": False,
        "priority": 5,
        "cooldown": 60.0
    },
    {
        "task_name": "Click  [Earse Play Data] [Reroll Earse GameData]",
        "type": "pixel",
        "click_location_str": "860,367",
        "search_array": ["887,365","#ffffff","842,368","#ffffff","861,381","#e60012","932,367","#3d4958"],
        "isLogical": False,
        "priority": 1,
        "cooldown": 3.0
    },
    {
        "task_name": "Confirm Erase Data [Reroll Earse GameData]",
        "type": "pixel",
        "click_location_str": "619,490",
        "search_array": ["249,35","#0d12b5","263,47","#e60012","234,98","#ffff00","584,489","#ffffff","645,490","#ffffff",],
        "isLogical": False,
        "priority": 1,
        "cooldown": 3.0,
        "json_Reroll_Earse_GameData": True,  # Mark this reroll task as complete
        "Reroll_Tutorial_FirstMatch_Tasks": True  # Switch to next task set
    },
]
