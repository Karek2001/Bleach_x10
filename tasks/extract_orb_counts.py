Extract_Orb_Counts_Tasks = [
    {
        "task_name": "Ultra Robust Orb Extraction",
        "type": "ultra_robust_orb",  # New special type
        "priority": 1,
        "cooldown": 60.0,
        "pre_delay": 3,  # Wait for screen to stabilize
        "click_location_str": "93,23",
        "Extract_Account_ID_Tasks": True  # Move to next task set after successful extraction
    }
]
    