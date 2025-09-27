Recive_Giftbox_Orbs_Check = [
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
        "task_name": "From [Gifts] To [Soul Tickets] [Recive Giftbox Orbs]",
        "type": "pixel",
        "click_location_str": "382,79",
        "search_array": ["189,87","#464ac6","324,80","#616060"],
        
        "priority": 25,
        "cooldown": 5.0,
        "Recive_Giftbox_Orbs_Tasks": True,
        "sleep": 3,
    },
        {
        "task_name": "From [Soul Tickets] To [Characters] [Recive Giftbox Orbs]",
        "type": "pixel",
        "click_location_str": "568,82",
        "search_array": ["321,81","#6365ce","503,80","#616060"],
        
        "priority": 25,
        "cooldown": 5.0,
        "Recive_Giftbox_Orbs_Tasks": True,
        "sleep": 3,
    },
        {
        "task_name": "From [Characters] To [Friend Points] [Recive Giftbox Orbs]",
        "type": "pixel",
        "click_location_str": "743,79",
        "search_array": ["500,81","#6365ce","670,80","#616060"],
        
        "priority": 25,
        "cooldown": 5.0,
        "Recive_Giftbox_Orbs_Tasks": True,
        "sleep": 3,
    },

            {
        "task_name": "All Gifts Are Recived [Recive Giftbox Orbs]",
        "type": "pixel",
        "click_location_str": "486,487",
        "search_array": ["462,72","#727171","461,72","#727171","638,72","#727171","812,72","#8789d9"],
        
        "priority": 1,
        "cooldown": 5.0,
        "json_Recive_Giftbox_Orbs": True,  # Mark task as complete in device state
        "ScreenShot_MainMenu_Tasks": True,
        "sleep": 3,
    },

]