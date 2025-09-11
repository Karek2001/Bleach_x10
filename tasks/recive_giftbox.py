# tasks/recive_giftbox.py - Tasks for receiving gift box items

Recive_GiftBox = [
    # Navigate to Gift Box
    {
        "task_name": "Open Gift Box",
        "type": "template",
        "template_path": "templates/GiftBox/GiftBox_Icon.png",
        "roi": [850, 50, 100, 100],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
    },
    
    # Select All Gifts
    {
        "task_name": "Select All Gifts",
        "type": "template",
        "template_path": "templates/GiftBox/Select_All.png",
        "roi": [100, 450, 200, 60],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "priority": 15,
        "cooldown": 5.0,
    },
    
    # Receive Selected Gifts
    {
        "task_name": "Receive All Selected Gifts",
        "type": "template",
        "template_path": "templates/GiftBox/Receive.png",
        "roi": [650, 450, 200, 60],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "priority": 20,
        "cooldown": 5.0,
    },
    
    # Confirm Receipt
    {
        "task_name": "Confirm Gift Receipt",
        "type": "pixel",
        "click_location_str": "480,372",
        "search_array": ["385,152","#191925","522,153","#191925","480,370","#ffffff"],
        "isLogical": False,
        "priority": 25,
        "cooldown": 5.0,
    },
    
    # Check if gift box is empty
    {
        "task_name": "Gift Box Empty - All Received",
        "type": "pixel",
        "click_location_str": "480,480",
        "search_array": ["480,250","#808080","480,300","#808080","480,350","#808080"],
        "isLogical": False,
        "json_Recive_GiftBox": True,
        "Skip_Kon_Bonaza_Tasks": True,  # Move to next task set
        "priority": 30,
        "cooldown": 5.0,
    },
    
    # Exit Gift Box
    {
        "task_name": "Exit Gift Box",
        "type": "pixel",
        "click_location_str": "25,25",
        "search_array": ["25,25","#ffffff","50,25","#ffffff","75,25","#ffffff"],
        "isLogical": False,
        "BackToRestartingTasks": True,
        "priority": 35,
        "cooldown": 5.0,
    },
]