# tasks/skip_kon_bonaza.py - Tasks for skipping Kon Bonanza 100 times

Skip_Kon_Bonaza = [

{
    "task_name": "Leave Gift Box If we are still there",
    "type": "pixel",
    "click_location_str": "475,488",
    "search_array": ["794,36","#0d12b5","780,49","#e60012","431,37","#191925","582,493","#2762fa"],
    "isLogical": False,
    "shared_detection": True,
    "priority": 10,
    "cooldown": 5.0,
        "sleep": 3,
},



    # Navigate to Kon Bonanza
    {
        "task_name": "Open [Solo] Menu For Kon Bonanza",
        "type": "pixel",
        "click_location_str": "892,493",
        "search_array": ["893,485","#978e74","891,498","#978e74","868,500","#978e74","874,529","#dce0fd"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Click [Powerup Quests]",
        "type": "pixel",
        "click_location_str": "507,299",
        "search_array": ["450,288","#ffffff","534,308","#ffffff","552,315","#981400","531,323","#2e0d02"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
        {
        "task_name": "Click [Kon Bonaza]",
        "type": "template",
        "template_path": "templates/KonBonaza/KonBonaza.png",
        "roi": [71, 45, 408, 489],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
    },
        {
        "task_name": "Click [Normal Mode]",
        "type": "pixel",
        "click_location_str": "673,488",
        "search_array": ["646,492","#ffffff","716,490","#ffffff","759,480","#0a37e7"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
           {
        "task_name": "Start a Match That First Time Played [Kon Bonaza]",
        "type": "pixel",
        "click_location_str": "726,496",
        "search_array": ["435,513","#fe0706","526,513","#f3605c","799,493","#0a3ae1"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
               {
        "task_name": "Start a Match That 10x Skip Tickets [Kon Bonaza]",
        "type": "pixel",
        "click_location_str": "734,495",
        "search_array": ["492,490","#ffffff","507,489","#ffffff","560,483","#ea5405","506,498","#ffc130"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
                   {
        "task_name": "Click [Set Tickets] [Kon Bonaza]",
        "type": "pixel",
        "click_location_str": "507,490",
        "search_array": ["500,349","#191925","481,491","#ffffff","508,489","#ffffff","510,499","#e60012"],
        "isLogical": False,
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                   {
        "task_name": "Increase The Tickets Until IT Reachs 10x [Kon Bonaza]",
        "type": "pixel",
        "click_location_str": "594,423",
        "search_array": ["589,429","#01b801","595,423","#f4f4f4","600,429","#01b801"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
                       {
        "task_name": "After Finishing Match Click [Retry]",
        "type": "pixel",
        "click_location_str": "198,509",
        "search_array": ["699,508","#ffffff","752,507","#ffffff","763,510","#ffffff","823,499","#1643ec"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "Increment_Kon_Bonaza": True,
        "StopSupport":"json_Kon_Bonaza",
        "sleep": 3,
        

    },
                           {
        "task_name": "Click Title For Speed Up Completing [Kon Bonaza]",
        "type": "pixel",
        "click_location_str": "151,26",
        "search_array": ["254,25","#ffffff","457,27","#ffffff","139,25","#fafbfb"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },

                           {
        "task_name": "Click [Home] After Finishing 100 Match of Kon Bonaza",
        "type": "pixel",
        "click_location_str": "389,511",
        "search_array": ["357,506","#ffffff","368,507","#ffffff","450,505","#0939e0"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
        "ConditionalRun": ["Skip_Kon_Bonaza"],
        "Recive_GiftBox_Tasks": True,
        "sleep": 3,

    },


]


