# tasks/recive_giftbox.py - Tasks for receiving gift box items

Recive_GiftBox = [
    # Navigate to Gift Box
    {
        "task_name": "Open Gift Box",
        "type": "pixel",
        "click_location_str": "910,165",
        "search_array": ["899,179","#d42929","873,190","#ffffff","941,189","#ffffff","910,173","#fcf9f4"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
    },
    
    {
        "task_name": "Click [Collect All Page]",
        "type": "pixel",
        "click_location_str": "221,484",
        "search_array": ["127,486","#ffffff","183,494","#57626f","236,494","#57626f"],
        "isLogical": False,
        "priority": 15,
        "cooldown": 5.0,
    },
    
    {
        "task_name": "Click [Confirm Select Gift Page]",
        "type": "pixel",
        "click_location_str": "621,372",
        "search_array": ["723,154","#0d12b5","714,165","#e60012","432,152","#191925","518,157","#191925"],
        "isLogical": False,
        "priority": 20,
        "cooldown": 5.0,
    },
    
    # Confirm Receipt
    {
        "task_name": "Menu Collect All Gifts Click [Close]",
        "type": "pixel",
        "click_location_str": "472,485",
        "search_array": ["242,34","#0d12b5","265,48","#e60012","383,36","#191925","523,37","#191925","576,43","#191925","312,80","#ffffff"],
        "isLogical": False,
        "priority": 25,
        "cooldown": 5.0,
    },
        {
        "task_name": "Menu Collect All Gifts Click [Close] [For Single Gift]",
        "type": "pixel",
        "click_location_str": "478,483",
        "search_array": ["384,37","#191925","713,34","#0d12b5","700,47","#e60012","609,477","#1b46f0"],
        "isLogical": False,
        "priority": 25,
        "cooldown": 5.0,
    },
        {
        "task_name": "All Gifts Recived From Currently Section Let's Switch To Check",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["781,488","#fdfbfb","300,482","#252b31","267,474","#7f7f7f","832,488","#fdfbfb"],
        "isLogical": False,
        "priority": 30,
        "cooldown": 5.0,
        "sleep": 2.0,
        "Recive_GiftBox_Check_Tasks": True,
        "ShowsIn": ["recive_giftbox"],
    },
    {
        "task_name": "Reached Maximum Tickets Click [Close] [Kon Bonaza]",
        "type": "pixel",
        "click_location_str": "482,489",
        "search_array": ["263,433","#ff0000","363,480","#1341ea"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
    },
    {
        "task_name": "Tickets Are Fully. Let's Spend The 1000 Tickets In Kon Event",
        "type": "pixel",
        "click_location_str": "477,375",
        "search_array": ["702,152","#0d12b5","701,166","#e60012","432,152","#191925","499,275","#ffffff","517,272","#ffffff","538,274","#ffffff"],
        "isLogical": False,
        "priority": 1,
        "cooldown": 5.0,
        "Skip_Kon_Bonaza_Tasks": True,
    },


]