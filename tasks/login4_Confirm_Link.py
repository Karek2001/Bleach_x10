Login4_Confirm_Link_Tasks = [
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
        "task_name": "Click [Login Button] [Confirm Link]",
        "type": "template",
        "template_path": "templates/Login/LoginButton.png",
        "roi": [250, 304, 473, 209],
        "use_match_position": True,
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 2.0
    },
        {
        "task_name": "Click [Link With App] [Confirm Link]",
        "type": "template",
        "template_path": "templates/Login/LinkWithApp.png",
        "roi": [139, 409, 734, 130],
        "use_match_position": True,
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 2.0
    },
            {
        "task_name": "Click [OK] For  Warning Linking Email With Account [Confirm Link]",
        "type": "pixel",
        "click_location_str": "621,494",
        "search_array": ["820,37","#0d12b5","803,50","#e60012","431,44","#191919","532,45","#191919","532,45","#191919","532,45","#191919","603,493","#ffffff"],
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 2.0
    },
                {
        "task_name": "Click [OK] For  Login Confirm [Confirm Link]",
        "type": "pixel",
        "click_location_str": "481,371",
        "search_array": ["712,153","#0d12b5","703,166","#e60012","432,152","#191925","426,259","#ffffff","533,266","#ffffff"],
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 2.0
    },
                    {
        "task_name": "Detect Account Already Linked! [Confirm Link]",
        "type": "pixel",
        "click_location_str": "480,497",
        "search_array": ["716,43","#0d12b5","700,55","#e60012","547,158","#ffffff","661,161","#ffffff","704,160","#ffffff","714,158","#dc0d0d"],
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 2.0,
        "Endgame_Tasks": True,
        "json_isLinked": True,
        "sync_to_airtable": True,
    },
]
