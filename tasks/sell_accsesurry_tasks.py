# tasks/sell_characters_tasks.py - Complete tasks for selling excess characters

Sell_Accessury = [
    
    # Selling process - Sequential steps
    {
        "task_name": "Click [Sell]",
        "type": "pixel",
        "click_location_str": "153,515",
        "search_array": ["141,516","#eaeaea","168,515","#ffffff","132,513","#2b3a48"],
        "isLogical": False,
        "priority": 15,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Click [Multi Select]",
        "type": "pixel",
        "click_location_str": "319,511",
        "search_array": ["218,521","#ffbc2e","276,513","#d9dada","291,511","#f9f9fa","857,516","#16337d"],
        "isLogical": False,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Click [3 Stars]",
        "type": "pixel",
        "click_location_str": "485,204",
        "search_array": ["436,202","#ffffff","490,202","#ffffff","426,191","#5e666d","433,217","#e60012"],
        "isLogical": False,
        "priority": 30,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Click [Select 50 Characters]",
        "type": "pixel",
        "click_location_str": "665,489",
        "search_array": ["426,207","#ec4d01","404,315","#ec4d01","582,495","#2964fa","768,495","#2964fa"],
        "isLogical": False,
        "priority": 35,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Click [Sell]",
        "type": "pixel",
        "click_location_str": "817,510",
        "search_array": ["806,509","#ffffff","832,510","#ffffff","859,506","#0a3ae1"],
        "isLogical": False,
        "priority": 40,
        "cooldown": 5.0,
        "sleep": 3,
    },
    
    # Confirmation steps
    {
        "task_name": "Click [OK To Sell]",
        "type": "pixel",
        "click_location_str": "621,486",
        "search_array": ["603,486","#ffffff","622,489","#ffffff","225,433","#191925","686,485","#0939e0"],
        "isLogical": False,
        "priority": 45,
        "cooldown": 5.0,  # Longer cooldown to ensure sale processes
    },
    {
        "task_name": "Click [Close]",
        "type": "template",
        "template_path": "templates/Sell_Characters/Close.png",
        "roi": [370, 169, 115, 58],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "shared_detection": True,
        "priority": 50,
        "cooldown": 5.0,
    },

    {
        "task_name": "Leave No More Accessury To Sell",
        "type": "pixel",
        "click_location_str": "25,21",
        "search_array": ["210,516","#222930","220,512","#7f7f7f","188,523","#730009","343,129","#f05801"],
        "isLogical": False,
        "priority": 51,
        "cooldown": 5.0,
        "BackToRestartingTasks": True,
        "sleep": 3,
    },
]