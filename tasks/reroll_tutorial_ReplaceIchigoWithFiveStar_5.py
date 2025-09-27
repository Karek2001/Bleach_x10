# reroll_tutorial_ReplaceIchigoWithFiveStar_5.py - Replace Ichigo with 5-star character
reroll_replaceichigowithfivestar_tasks = [
       {
        "task_name": "Click [Thank You] For Mod Menu [Replace Ichigo With FiveStar]",
        "type": "pixel",
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
         {
        "task_name": "Click [Game Start] [Replace Ichigo With FiveStar]",
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
        "task_name": "Rokiia Is Talking [Replace Ichigo With FiveStar]",
        "type": "pixel",
        "click_location_str": "449,481",
        "search_array": ["238,152","#282828","232,213","#fad2c2","236,259","#fad2c2"],
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Click [Edit] [Replace Ichigo With FiveStar]",
        "type": "pixel",
        "click_location_str": "382,507",
        "search_array": ["387,479","#e1773a","368,462","#323348"],
        "priority": 1,
        "cooldown": 2.0
    },
    {
        "task_name": "Switch From [Party 1] To [Party 2] [Replace Ichigo With FiveStar]",
        "type": "pixel",
        "click_location_str": "278,78",
        "search_array": ["211,75","#4767d4","209,85","#e60012","193,77","#ffffff","299,78","#405761","293,86","#e60012"],
        "priority": 2,
        "cooldown": 6.0
    },
    {
        "task_name": "Swipe Aizen To Be Main Character [Replace Ichigo With FiveStar]",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["142,190","#ececef","145,223","#e8e9eb","300,79","#425bcf","510,157","#523d38","485,193","#edc7b2"],
        "shared_detection": True,
        "min_matches_for_swipe": 1,
        "swipe_command": "shell input swipe 489 212 253 211 2000",
        "priority": 3,
        "cooldown": 20.0
    },
    {
        "task_name": "Check is Aizen Main And is we Party2 And Leave [Replace Ichigo With FiveStar]",
        "type": "pixel",
        "click_location_str": "24,23",
        "search_array": ["299,79","#425bcf","146,190","#eec8b5","170,158","#523d38""282,86","#e60012"],
        "priority": 4,
        "cooldown": 10.0,
        "sleep": 5,
        "json_Reroll_ReplaceIchigoWithFiveStar": True,
        "BackToStory": True
    },

]
