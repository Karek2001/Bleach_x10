Login3_Wait_For_2FA_Tasks = [


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
        "task_name": "Detect 2FA Code Request [Wait for 2FA]",
        "type": "pixel",
        "click_location_str": "0,0",  # Detection only
        "search_array": ["246,377","#23aabc","239,376","#edf1f2"],  # 2FA screen
        "priority": 1,
        "cooldown": 5.0,
        "shared_detection": True,
        "min_matches_for_swipe": 1,
        "swipe_command": "shell input swipe 443 400 443 140 900",
        "sleep": 3
    },
    {
        "task_name": "Enter 2FA Code [Wait for 2FA]",
        "type": "template",
        "template_path": "templates/Login/VerificationCode.png",
        "roi": [276, 202, 404, 176],
        "use_match_position": True,
        "DownPixels": 35,
        "priority": 5,
        "cooldown": 5.0,
        "sleep": 3,
        "Confirm_2FA_Code_Tasks": True,
        "Get_2fa": True,
        "Login4_Confirm_Link_Tasks": True,
    },
]
