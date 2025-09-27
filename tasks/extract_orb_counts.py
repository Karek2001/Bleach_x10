Extract_Orb_Counts_Tasks = [
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
        "task_name": "Ultra Robust Orb Extraction",
        "type": "ultra_robust_orb",  # New special type
        "priority": 1,
        "cooldown": 60.0,
        "pre_delay": 3,  # Wait for screen to stabilize
        "click_location_str": "93,23",
        "Extract_Account_ID_Tasks": True  # Move to next task set after successful extraction
    }
]
    