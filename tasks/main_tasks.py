# tasks/main_tasks.py - Main story progression tasks

Main_Tasks = [
    {
        "task_name": "Click Story MAP",
        "type": "template",
        "template_path": "templates/StoryMAP.png",
        "roi": [3, 127, 956, 347],
        "confidence": 0.75,
        "use_match_position": True,
        "isLogical": False,
        "shared_detection": True,  # Check with other templates in same frame
        "priority": 10,  # Higher priority
    },
    {
        "task_name": "Click [Feet Story Map]",
        "type": "template",
        "template_paths": [
            "templates/FeetStoryMap.png",
            "templates/FeetStoryMap2.png",
            "templates/FeetStoryMap3.png"
        ],
        "roi": [1, 131, 956, 346],
        "confidence": 0.70,
        "use_match_position": True,
        "isLogical": False,
        "shared_detection": True,  # Check with other templates
        "priority": 10,
    },
    {
        "task_name": "All Possible Ways of Stars Map #1",
        "type": "template",
        "template_path": "templates/Stars.png",
        "roi": [3, 86, 953, 415],
        "confidence": 0.70,
        "use_match_position": True,
        "multi_click": True,  # Click ALL matches found
        "shared_detection": True,  # Check with other templates
        "isLogical": False,
        "UpPixels": 20,
        "priority": 15,
    },
    
    # Regular tasks without shared detection (checked one by one)
    {
        "task_name": "Click [Prepare To Battle]",
        "type": "template",
        "template_path": "templates/Prepare.png",
        "roi": [507, 458, 313, 60],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "priority": 20,
        # No shared_detection flag - processed sequentially
    },
    {
        "task_name": "Click [Start Quest]",
        "type": "pixel",
        "click_location_str": "715,497",
        "search_array": ["583,490","#ffffff","652,491","#0d3de4","671,498","#ffffff","735,496","#ffffff"],
        "isLogical": False,
        "priority": 25,
    },

]