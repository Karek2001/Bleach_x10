# tasks/hard_story.py - Advanced Hard Story progression tasks

HardStory_Tasks = [
    {
        "task_name": "Active Hard Mode If It Doesn't Activited",
        "type": "pixel",
        "click_location_str": "845,41",
        "search_array": ["921,42","#0a36e5","47,15","#010101","24,49","#e50012","81,32","#fefefe"],
        "isLogical": False,
        "priority": 15,
    },
    {
        "task_name": "Hard Mode Activited Let Swipe!",
        "type": "pixel",
        "click_location_str": "0,0",  # No click needed, just detection
        "search_array": ["921,40","#fe7272","47,15","#010101","24,49","#e50012","81,32","#fefefe"],
        "isLogical": True,
        "HardModeSwipe": True,  # Flag to identify this as hard mode swipe task
        "shared_detection": True,
        "priority": 15,
        "cooldown": 2.0,
    },
    {
        "task_name": "Let's Start With Part-1 HARD!",
        "type": "template",
        "template_path": "templates/Story_Mode_Hard/Part1_hard.png",
        "roi": [135, 113, 491, 290],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": True,
        "shared_detection": True,
        "priority": 5,
        "cooldown": 2.0,
        "BackToStory": True,
    },
    
]