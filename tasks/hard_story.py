# tasks/hard_story.py - Advanced Hard Story progression tasks

HardStory_Tasks = [
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
        "task_name": "Part 24 [Side Story] Hard Finished [Switch To Sub Stories]",
        "type": "pixel",
        "click_location_str": "34,29",
        "search_array": ["537,344","#ff0000","918,42","#eb1a1a","506,364","#e9e902","486,148","#f5cd3d"],
        
        "priority": 1,
        "Sub-Stores": True,
        "KeepChecking": 5.0,
        "json_EasyMode": True,
        "json_HardMode": True,
        "json_SideMode": True,
        "sleep": 3,
    },
    {
        "task_name": "Active Hard Mode If It Doesn't Activited",
        "type": "pixel",
        "click_location_str": "845,41",
        "search_array": ["921,42","#0a36e5","47,15","#010101","24,49","#e50012","81,32","#fefefe"],
        
        "priority": 20,
        "sleep": 3,
    },
    {
        "task_name": "Hard Mode Activited Let Swipe!",
        "type": "pixel",
        "click_location_str": "0,0",  # No click needed, just detection
        "search_array": ["921,40","#fe7272","47,15","#010101","24,49","#e50012","81,32","#fefefe"],
        "isLogical": True,
        "HardModeSwipe": True,  # Flag to identify this as hard mode swipe task
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
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
        "priority": 20,
        "cooldown": 5.0,
        "BackToStory": True,
        "json_EasyMode": True,
    },
        {
        "task_name": "Let's Start With Part-1 HARD! [Side Story]",
        "type": "template",
        "template_path": "templates/Story_Mode_Hard/S_Part1_hard.png",
        "roi": [10, 79, 949, 351],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": True,
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "BackToStory": True,
        
    },

    
]