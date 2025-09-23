Endgame_Tasks = [
    {
        "task_name": "Main Menu Navigation [Endgame]",
        "type": "pixel",
        "click_location_str": "960,540",
        "search_array": ["960,540","#000000"],  # Always matches for now
        "priority": 1,
        "cooldown": 10.0,
        "sleep": 5.0
    },
    {
        "task_name": "Post-Link Progression Check [Endgame]",
        "type": "pixel", 
        "click_location_str": "0,0",  # Detection only
        "search_array": ["500,300","#FF0000"],  # Placeholder detection
        "priority": 2,
        "cooldown": 15.0,
        "sleep": 3.0
    }
]
