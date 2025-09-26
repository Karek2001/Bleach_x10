# tasks/skip_kon_bonaza.py - Tasks for skipping Kon Bonanza 100 times

Kon_Bonaza_1Match_Tasks = [
                               {
        "task_name": "Click [Home] After Finishing 1 Match of Kon Bonaza",
        "type": "pixel",
        "click_location_str": "389,511",
        "search_array": ["357,506","#ffffff","368,507","#ffffff","450,505","#0939e0"],
        
        "priority": 1,
        "cooldown": 5.0,
        "Upgrade_Characters_Level_Tasks": True,
        "sleep": 3,

    },

    # Navigate to Kon Bonanza
        {
        "task_name": "Click [Kon Bonaza Event] [Kon Bonaza 1 Match]",
        "type": "template",
        "template_path": "templates/KonBonaza/KonBonaza.png",
        "roi": [71, 45, 408, 489],
        "confidence": 0.90,
        "use_match_position": True,
        
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
        {
        "task_name": "Click [Normal Mode] [Kon Bonaza 1 Match]",
        "type": "pixel",
        "click_location_str": "673,488",
        "search_array": ["646,492","#ffffff","716,490","#ffffff","759,480","#0a37e7"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
               {
        "task_name": "Start a Match That 10x Skip Tickets [Kon Bonaza]",
        "type": "pixel",
        "click_location_str": "734,495",
        "search_array": ["492,490","#ffffff","507,489","#ffffff","560,483","#ea5405","506,498","#ffc130"],
        
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
                   {
        "task_name": "Click [Set Tickets] [Kon Bonaza]",
        "type": "pixel",
        "click_location_str": "507,490",
        "search_array": ["500,349","#191925","481,491","#ffffff","508,489","#ffffff","510,499","#e60012"],
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
                   {
        "task_name": "Increase The Tickets Until IT Reachs 10x [Kon Bonaza]",
        "type": "pixel",
        "click_location_str": "594,423",
        "search_array": ["589,429","#01b801","595,423","#f4f4f4","600,429","#01b801"],
        
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
                           {
        "task_name": "Click Title For Speed Up Completing [Kon Bonaza]",
        "type": "pixel",
        "click_location_str": "151,26",
        "search_array": ["254,25","#ffffff","457,27","#ffffff","139,25","#fafbfb"],
        
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },




]


