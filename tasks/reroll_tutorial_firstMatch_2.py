# reroll_tutorial_firstMatch_2.py - Tutorial first match tasks
reroll_tutorial_firstmatch_tasks = [
       {
        "task_name": "Click [Thank You] For Mod Menu [Reroll First Match]",
        "type": "pixel",
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        # DUMMY TASK FOR TEST - marks first match complete
        "task_name": "Click  [Earse Play Data] [Reroll First Match]",
        "type": "pixel",
        "click_location_str": "860,367",
        "search_array": ["887,365","#ffffff","842,368","#ffffff","861,381","#e60012","932,367","#3d4958"],
        "isLogical": False,
        "priority": 1,
        "cooldown": 2.0,
        "json_Reroll_Tutorial_FirstMatch": True,  # Mark this reroll task as complete
        "Reroll_Tutorial_CharacterChoose_Tasks": True  # Switch to character choose
    },
    # {
    #     "task_name": "Tutorial Victory Screen",
    #     "type": "pixel",
    #     "click_location_str": "480,500",
    #     "search_array": ["450,480","#ffc107","510,480","#ffc107","480,500","#ffffff"],
    #     "isLogical": False,
    #     "priority": 5,
    #     "cooldown": 3.0,
    #     "json_Reroll_Tutorial_FirstMatch": True,
    #     "Reroll_Tutorial_CharacterChoose_Tasks": True  # Switch to character choose
    # },
    # {
    #     "task_name": "Tutorial Rewards Screen",
    #     "type": "pixel",
    #     "click_location_str": "480,520",
    #     "search_array": ["450,500","#4caf50","510,500","#4caf50","480,520","#ffffff"],
    #     "isLogical": False,
    #     "priority": 6,
    #     "cooldown": 2.0,
    #     "json_Reroll_Tutorial_FirstMatch": True,
    #     "Reroll_Tutorial_CharacterChoose_Tasks": True
    # }
]
