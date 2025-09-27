# reroll_tutorial_CharacterChoose_3.py - Character selection in tutorial
reroll_tutorial_characterchoose_tasks = [
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
        "task_name": "Click [Skip] When Showed [Reroll Character Choose]",
        "type": "pixel",
        "click_location_str": "900,29",
        "search_array": ["909,32","#ffffff","897,37","#e60012","936,30","#485159"],
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
       {
        "task_name": "Click [Skip] For Character Unlocked! [Aizen] [Reroll Character Choose]",
        "type": "pixel",
        "click_location_str": "912,18",
        "search_array": ["901,18","#ffffff","919,21","#ffffff","924,25","#e60012"],
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },

   {
        "task_name": "Click [Thank You] For Mod Menu [Reroll Character Choose]",
        "type": "pixel",
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
         {
        "task_name": "Click [Game Start] [Reroll Character Choose]",
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
        "task_name": "Click [Character Summon] [Reroll Character Choose]",
        "type": "pixel",
        "click_location_str": "78,489",
        "search_array": ["63,523","#ffffff","54,494","#31323a","35,486","#31323a"],
        "priority": 1,
        "cooldown": 30.0
    },
            {
        "task_name": "Click [Select Free Summon] [Reroll Character Choose]",
        "type": "pixel",
        "click_location_str": "600,464",
        "search_array": ["613,482","#00ff00","648,482","#00ff00","616,501","#ffffff"],
        "priority": 1,
        "cooldown": 30.0
    },
                {
        "task_name": "Select [Aizen FREE 5 STAR] [Reroll Character Choose]",
        "type": "pixel",
        "click_location_str": "374,356",
        "search_array": ["393,338","#513d38","376,366","#ecc5b1","342,326","#ffffff","609,493","#122f7c"],
        "priority": 1,
        "cooldown": 30.0
    },
                {
        "task_name": "Click [Select] Confirm Aizen Select [Reroll Character Choose]",
        "type": "pixel",
        "click_location_str": "488,487",
        "search_array": ["333,329","#00ff00","447,491","#ffffff","610,491","#1f58f9"],
        "priority": 1,
        "cooldown": 30.0
    },
                {
        "task_name": "Click [OK] To Confirm Using Free Ticket For AIZEN 5 STAR [Reroll Character Choose]",
        "type": "pixel",
        "click_location_str": "621,370",
        "search_array": ["258,147","#0d12b5","267,159","#e60012","282,326","#ff0000","675,327","#ff0000","641,270","#ffeb04"],
        "priority": 1,
        "cooldown": 30.0
    },
                {
        "task_name": "Click [Green House] [Reroll Character Choose]",
        "type": "pixel",
        "click_location_str": "30,298",
        "search_array": ["642,87","#513c37","623,119","#edc7b2","43,279","#65a92e"],
        "priority": 1,
        "cooldown": 30.0,
        "json_Reroll_Tutorial_CharacterChoose": True,  # Mark this reroll task as complete
        "Reroll_Tutorial_CharacterChoosePart2_Tasks": True,  # Switch to Character Choose Part 2
    },

]
