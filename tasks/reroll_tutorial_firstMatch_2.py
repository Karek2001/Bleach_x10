# reroll_tutorial_firstMatch_2.py - Tutorial first match tasks
reroll_tutorial_firstmatch_tasks = [
       {
        "task_name": "Click [Thank You] For Mod Menu [Reroll First Match]",
        "type": "pixel",
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
         {
        "task_name": "Click [Game Start] [Reroll First Match]",
        "type": "template",
        "template_path": "templates/Reroll/GameStart.png",
        "roi": [350, 432, 274, 35],
        "confidence": 0.80,
        "use_match_position": True,
        "priority": 15,
        "cooldown": 50.0,
        "sleep": 3,
    },
     {
        "task_name": "Detect First Match Has Been Started! Let's Switch To First Match Tasks [Reroll Earse GameData Part 2]",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["51,22","#ffaa4e","59,51","#eec2b0"],
        "priority": 1,
        "cooldown": 30.0,
        "First_Match_Script": True,
    },
        {
        "task_name": "Click [New Record] [Reroll Earse GameData Part 2]",
        "type": "pixel",
        "click_location_str": "540,489",
        "search_array": ["834,35","#ff0000","839,60","#ffffff","580,28","#ffffff","183,362","#ffad42"],
        "priority": 1,
        "cooldown": 2.0
    },
            {
        "task_name": "Click [Home] [Reroll Earse GameData Part 2]",
        "type": "pixel",
        "click_location_str": "394,511",
        "search_array": ["357,508","#ffffff","408,509","#ffffff","450,510","#2059f9","236,28","#ffffff"],
        "priority": 1,
        "cooldown": 2.0,
        "json_Reroll_Tutorial_FirstMatch": True,  # Mark this reroll task as complete
        "Reroll_Tutorial_CharacterChoose_Tasks": True  # Switch to character choose
    },
          {
        "task_name": "Rokiia Is Talking [When Game Restarted We May See Rokia Talking][Reroll First Match]",
        "type": "pixel",
        "click_location_str": "449,481",
        "search_array": ["238,152","#282828","232,213","#fad2c2","236,259","#fad2c2"],
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
        "json_Reroll_Tutorial_FirstMatch": True,  # Mark this reroll task as complete
        "Reroll_Tutorial_CharacterChoose_Tasks": True  # Switch to character choose
    },
]
