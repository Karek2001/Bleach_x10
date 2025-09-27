Sort_Filter_Ascension_Tasks = [
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
        "task_name": "Click [Edit] [Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "384,494",
        "search_array": ["380,481","#e1773a","367,462","#323348","362,524","#ffffff"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
        {
        "task_name": "Choose [Any Character] [Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "483,200",
        "search_array": ["74,24","#ffffff","106,25","#ffffff","24,20","#ffffff","855,513","#56390d"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
            {
        "task_name": " Click [Power Up][Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "197,491",
        "search_array": ["151,496","#ffffff","229,496","#ffffff","236,475","#31fc24"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
            {
        "task_name": " Click [Soul Tree] [Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "120,209",
        "search_array": ["851,239","#90909c","585,235","#90909c","323,231","#90909c"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
            {
        "task_name": "Click [Level] [Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "378,209",
        "search_array": ["119,211","#00ff00","591,243","#90909c","851,234","#90909c"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
            {
        "task_name": "Click [Ascension] [Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "636,210",
        "search_array": ["120,211","#00ff00","378,211","#00ff00","849,242","#90909c"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
            {
        "task_name": " Click [Confirm][Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "647,493",
        "search_array": ["120,211","#00ff00","378,211","#00ff00","636,211","#00ff00"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
            {
        "task_name": " Click [Sort] [Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "766,38",
        "search_array": ["123,39","#191925","255,38","#191925","467,39","#191925","762,40","#ffffff"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
            {
        "task_name": "Sort From [ASC] To [DESC] [Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "289,415",
        "search_array": ["788,416","#ec4c01","402,415","#3e4e5f","258,100","#ef5201"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
            {
        "task_name": "Click [Filter] After Checking [Rarity + DESC] Are Selected [Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "432,36",
        "search_array": ["401,415","#e84b01","258,100","#ef5201"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                {
        "task_name": "Select [Level 4] [Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "585,252",
        "search_array": ["183,255","#e74901","622,254","#3e4957","582,251","#ffffff","598,256","#ffffff"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                   {
        "task_name": "Swipe 1x Time If [Level4+All] Selected [Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["296,158","#ff9800","622,256","#ea4b01","267,368","#ec4c01"],
        "shared_detection": True,
        "min_matches_for_swipe": 1,
        "swipe_command": "shell input swipe 443 400 443 140 900",
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 5,
    },
                       {
        "task_name": "Swipe 1x Time If [All+All] Are Showed UP [Sort Filter Ascension]",
        "type": "template",
        "template_path": "templates/Sort_Filter/Affliation.png",
        "roi": [349, 177, 278, 273],
        "shared_detection": True,
        "min_matches_for_swipe": 1,
        "swipe_command": "shell input swipe 443 400 443 140 900",
        
        "use_match_position": True,
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                    {
        "task_name": "Click [No Affiliction] [Sort Filter Ascension]",
        "type": "template",
        "template_path": "templates/Sort_Filter/NoAffiliation.png",
        "roi": [483, 61, 179, 254],
        "use_match_position": True,
        "delayed_click_location": "477,491",
        "delayed_click_delay": 2.0,
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                {
        "task_name": "Sort And Filter Are Sucessfully Done [Sort Filter Ascension]",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["856,37","#e14601","675,37","#e14601","754,37","#ffffff"],
        
        "priority": 1,
        "cooldown": 5.0,
        "json_Sort_Filter_Ascension": True,
        "Sort_Multi_Select_Garbage_First_Tasks": True,
        "sleep": 3,
    },
    
]
