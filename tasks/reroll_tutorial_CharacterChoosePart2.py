# reroll_tutorial_CharacterChoosePart2.py - Second part of reroll character choose process
reroll_tutorial_characterchoosepart2_tasks = [
    {
        "task_name": "Detect Game Updated! [Game Update]",
        "type": "pixel",
        "click_location_str": "480,373",
        "search_array": ["249,152","#0d12b5","264,166","#e60012","216,260","#ffffff","316,268","#ffffff","645,262","#ffffff","744,266","#ffffff"],
        "priority": 1,
        "cooldown": 999.0,
        "sleep": 3,
    },
    {
        "task_name": "Click [Skip] When Showed [Reroll Character Choose Part 2]",
        "type": "pixel",
        "click_location_str": "900,29",
        "search_array": ["909,32","#ffffff","897,37","#e60012","936,30","#485159"],
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
           {
        "task_name": "Click [Skip] For Character Unlocked! [Aizen] [Reroll Character Choose Part 2]",
        "type": "pixel",
        "click_location_str": "912,18",
        "search_array": ["901,18","#ffffff","919,21","#ffffff","924,25","#e60012"],
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
       {
        "task_name": "Click [Thank You] For Mod Menu [Reroll Character Choose Part 2]",
        "type": "pixel",
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
         {
        "task_name": "Click [Game Start] [Reroll Character Choose Part 2]",
        "type": "template",
        "template_path": "templates/Reroll/GameStart.png",
        "roi": [350, 432, 274, 35],
        "confidence": 0.70,
        "use_match_position": True,
        "priority": 15,
        "cooldown": 10.0,
        "sleep": 3,
    },
           {
        "task_name": "Rokiia Is Talking [Open Character Select]",
        "type": "pixel",
        "click_location_str": "449,481",
        "search_array": ["238,152","#282828","232,213","#fad2c2","236,259","#fad2c2"],
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
                "delayed_click_location": "449,481",
        "delayed_click_delay": 2.0,
    },
    {
        "task_name": "Click [Edit] For Adding Aizen in Party [Reroll Tutorial CharacterChoose Part 2]",
        "type": "pixel",
        "click_location_str": "384,511",
        "search_array": ["362,524","#ffffff","387,480","#e1773a","365,463","#323348"],
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Let's Swipe Aizen To Party! [Reroll Tutorial CharacterChoose Part 2]",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["253,194","#ececee","489,188","#ebc5b1","509,157","#513d38"],
        "priority": 2,
        "cooldown": 15.0,
        "shared_detection": True,
        "min_matches_for_swipe": 1,
        "swipe_command": "shell input swipe 489 212 253 211 2000",
        "sleep": 3
    },
    {
        "task_name": "Complete Character Choose Part 2 [Reroll Tutorial CharacterChoose Part 2]",
        "type": "pixel",
        "click_location_str": "30,28",  # Detection only
        "search_array": ["260,193","#ecc6b1","281,158","#513d38","24,22","#ffffff"],
        "priority": 0,
        "cooldown": 999.0,  # Run once only
        "json_Reroll_Tutorial_CharacterChoosePart2": True,  # Mark this reroll task as complete
        "Reroll_Tutorial_SecondMatch_Tasks": True  # Switch to second match
    }
]
