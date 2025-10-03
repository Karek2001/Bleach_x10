Sort_Characters_Lowest_Level_Tasks = [
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
        "task_name": "Click [Edit] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "384,494",
        "search_array": ["380,481","#e1773a","367,462","#323348","362,524","#ffffff"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },

        {
        "task_name": "Click [Sort] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "795,90",
        "search_array": ["866,92","#404b59","798,91","#ffffff","786,100","#e60012"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
            {
        "task_name": "Click [Link Slots] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "391,332",
        "search_array": ["342,332","#ffffff","393,333","#ffffff","370,332","#ffffff","450,333","#3d4c5a"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                {
        "task_name": "Change Sort From [ASC] To [DESC] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "291,414",
        "search_array": ["248,413","#ffffff","359,420","#ffffff","405,415","#414e5c"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                    {
        "task_name": "Click [Filter] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "428,36",
        "search_array": ["403,416","#ec4c01","451,334","#ec4c01"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                        {
        "task_name": "Click [1 Star] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "260,254",
        "search_array": ["252,252","#ffffff","291,255","#3e4d5c"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                            {
        "task_name": "Click [2 Star] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "371,254",
        "search_array": ["362,252","#ffffff","400,255","#3d4d5c"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                            {
        "task_name": "Click [3 Star] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "481,254",
        "search_array": ["471,252","#ffffff","510,255","#3e4d5c"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                            {
        "task_name": "Click [4 Star] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "590,254",
        "search_array": ["581,252","#ffffff","622,256","#434f5c"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                            {
        "task_name": "Click [5 Star] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "699,254",
        "search_array": ["691,252","#ffffff","731,256","#424f5c"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                        {
        "task_name": "Swipe To Filtering By Powering UP [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["293,257","#ec4d01","402,257","#ec4d01","512,257","#ec4d01","622,257","#ec4d01","732,256","#ea4b01"],
        
        "priority": 1,
        "cooldown": 5.0,
        "swipe_count": 5,
        "swipe_command": "shell input swipe 443 400 443 140 900",
        "sleep": 3,
    },

                        {
        "task_name": "Find [Character PowerUP Status] And Clicks right 563-pixel [Sort by lowest level]",
        "type": "template",
        "template_path": "templates/Sort_Filter/CharacterPowerUpStatus.png",
        "confidence": 0.90,
        "roi": [98, 134, 293, 278],
        "use_match_position": True,
        "RightPixels": 563,
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                            {
        "task_name": "Swipe Down In [Character PowerUP Status] For [No Badge] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["308,45","#191920","653,52","#191920","546,123","#00ff00"],
        "priority": 1,
        "cooldown": 5.0,
        "swipe_count": 2,
        "swipe_command": "shell input swipe 443 400 443 140 900",
        "sleep": 3,
    },

                            {
        "task_name": "Click [No Badge] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "292,144",
        "search_array": ["554,51","#191920","283,159","#e60012","457,146","#3c4c5c"],
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },

                            {
        "task_name": "Click [SET] [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "716,478",
        "search_array": ["456,149","#ee5001","433,149","#ee5001","829,482","#225af9","698,480","#ffffff"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
        "delayed_click_location": "469,490",
        "delayed_click_delay": 5.0,
    }, 
                            {
        "task_name": "Detect Filter/Sort Are Implemented [Sort by lowest level]",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["749,91","#ffffff","782,91","#ffffff","871,88","#e34802"],
        
        "priority": 1,
        "cooldown": 5.0,
        "json_Sort_Characters_Lowest_Level": True,
        "Sort_Filter_Ascension_Tasks": True,
        "sleep": 3,
    },
]
