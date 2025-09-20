Extract_Account_ID_Tasks = [
        {
        "task_name": "Open AccountID menu if it doesn't opended [Extract Account ID]",
        "type": "pixel",
        "click_location_str": "87,26", 
        "search_array": ["899,485","#978e74","388,480","#e1773a","790,16","#593b0d"],  # Detect main menu
        "priority": 1,
        "cooldown": 30.0,
        "StopSupport": "json_AccountID",  # Skip if AccountID already extracted
    },
    {
        "task_name": "Search for Account ID",
        "type": "ocr",
        "roi": [0, 0, 1920, 1080],  # Search entire screen
        "use_match_position": False,
        "click_location_str": "0,0",  # No click, just search
        "is_id": True,
        "cooldown": 5.0,  # Reduced cooldown for faster retries
        "search_for_id_pattern": True,  # Special flag to keep searching for ID
        "extract_account_id_value": True,  # Extract and save to JSON
        "NextTaskSet_Tasks": True  # Continue to next task set when found
    }
]