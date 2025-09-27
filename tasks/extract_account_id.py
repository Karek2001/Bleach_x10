Extract_Account_ID_Tasks = [
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
        "task_name": "Open AccountID menu if it doesn't opened [Extract Account ID]",
        "type": "pixel",
        "click_location_str": "87,26", 
        "search_array": ["899,485","#978e74","388,480","#e1773a","790,16","#593b0d"],  # Detect main menu
        "priority": 1,
        "cooldown": 60.0,
        "StopSupport": "json_AccountID",  # Skip if AccountID already extracted
        "sleep": 10,
    },
    {
        "task_name": "Extract Account ID",
        "type": "ocr",
        "roi": [453, 7, 137, 54],
        "use_match_position": False,
        "click_location_str": "16,25",  # No click needed
        "is_id": True,
        "priority": 2,
        "cooldown": 60.0,
        "sleep": 3,
        "pre_delay": 2,
        "extract_account_id_value": True,  # Direct extraction and save
        "Login1_Prepare_For_Link_Tasks": True  # Trigger next task set
    }
]