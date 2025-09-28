# reroll_earse_gamedata_1.py - First reroll task to erase game data
reroll_earse_gamedata_tasks = [
          {
        "task_name": "Detect Account Is Logened no Data Erased Happen! [Reroll Earse GameData]",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["895,484","#978e74","61,76","#ffffff","442,20","#0f47ca"],
        "priority": 1,
        "cooldown": 10.0,
        "sleep": 3,
        "close_game": True,
    },
        {
        "task_name": "Detect Game Updated! [Game Update]",
        "type": "pixel",
        "click_location_str": "480,373",
        "search_array": ["249,152","#0d12b5","264,166","#e60012","216,260","#ffffff","316,268","#ffffff","645,262","#ffffff","744,266","#ffffff"],
        "priority": 20,
        "cooldown": 999.0,
        "sleep": 3,
        "delayed_click_location": "480,373",
        "delayed_click_delay": 8.0,
    },

       {
        "task_name": "Click [Skip] When Showed [Reroll Earse GameData]",
        "type": "pixel",
        "click_location_str": "900,29",
        "search_array": ["909,32","#ffffff","897,37","#e60012","936,30","#485159"],
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
       {
        "task_name": "Click [Thank You] For Mod Menu [Reroll Earse GameData]",
        "type": "pixel",
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Click [Menu] [Reroll Earse GameData]",
        "type": "pixel",
        "click_location_str": "858,505",
        "search_array": ["839,505","#ffffff","835,512","#e60012","871,504","#ffffff","940,504","#454c55"],
        
        "priority": 5,
        "cooldown": 60.0,
        "sleep": 3
    },
    {
        "task_name": "Click  [Earse Play Data] [Reroll Earse GameData]",
        "type": "pixel",
        "click_location_str": "860,367",
        "search_array": ["887,365","#ffffff","842,368","#ffffff","861,381","#e60012","932,367","#3d4958"],
        
        "priority": 1,
        "cooldown": 10.0,
        "sleep": 3
    },
    {
        "task_name": "Confirm Erase Data [Reroll Earse GameData]",
        "type": "pixel",
        "click_location_str": "619,490",
        "search_array": ["249,35","#0d12b5","263,47","#e60012","234,98","#ffff00","584,489","#ffffff","645,490","#ffffff",],
        
        "priority": 1,
        "cooldown": 10.0,
        "sleep": 3
    },
        {
        "task_name": "Last Confirm Erase Data [Reroll Earse GameData]",
        "type": "pixel",
        "click_location_str": "618,375",
        "search_array": ["248,152","#0d12b5","257,166","#e60012","366,151","#eb1f1f","436,152","#eb1f1f","584,157","#eb1f1f","584,373","#ffffff","644,370","#ffffff","684,377","#fd4343"],
        
        "priority": 1,
        "cooldown": 10.0,
        "sleep": 3
    },
        {
        "task_name": "Click [Confirm] For Play Data Earsed [Reroll Earse GameData]",
        "type": "pixel",
        "click_location_str": "484,371",
        "search_array": ["432,152","#191925","527,156","#191925","389,260","#ffffff","451,262","#ffffff","564,262","#ffffff","570,266","#ffffff","256,153","#0d12b5"],
        "priority": 1,
        "cooldown": 10.0,
        "sleep": 3,
        "json_Reroll_Earse_GameData": True,  # Mark this reroll task as complete
        "Reroll_Earse_GameDataPart2_Tasks": True  # Switch to Part 2 next
    },
     
]