# extract_account_id.py - Account ID Extraction Tasks
"""
Tasks for extracting player account ID from the game interface.
This runs after orb count extraction is complete.
"""

Extract_Account_ID_Tasks = [

    {
    "task_name": "Extract Account ID",
    "type": "ocr",
    "roi": [463, 7, 126, 40],
    "use_match_position": False,
    "click_location_str": "26,30",
    "is_id": True,
    "cooldown": 30.0,
    "extract_account_id_value": True,  # Special flag to extract account ID to JSON
    "NextTaskSet_Tasks": True  # This triggers the next task set progression
}
]
