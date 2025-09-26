# tasks/shared_tasks.py - Complete shared tasks with smart detection

Shared_Tasks = [
    # HIGHEST PRIORITY - Connection/Network Issues (Priority 1-5)
    {
        "task_name": "Connection Error - Retry-OutGame",
        "type": "template",
        "template_path": "templates/Shared/Retry_Connection_Blue.png",
        "roi": [64, 254, 888, 239],
        "confidence": 0.90,
        "use_match_position": True,
        
        "shared_detection": True,
        "priority": 1,
        "cooldown": 5.0,  # Long cooldown to prevent connection spam
    },
    {
        "task_name": "Connection Error - Retry-InsideGame",
        "type": "template",
        "template_path": "templates/Shared/Retry_Connection_Red.png",
        "roi": [64, 254, 888, 239],
        "confidence": 0.90,
        "use_match_position": True,
        
        "shared_detection": True,
        "priority": 1,
        "cooldown": 5.0,
    },
    {
        "task_name": "Click [Resume] When Game Stopped Randomly",
        "type": "template",
        "template_path": "templates/Shared/Resume.png",
        "roi": [592, 460, 165, 54],
        "confidence": 0.90,
        "use_match_position": True,
        
        "shared_detection": True,
        "priority": 2,
        "cooldown": 3.0,
    },
       {
        "task_name": "Detect Game Updated! [Game Update]",
        "type": "pixel",
        "click_location_str": "480,373",
        "search_array": ["249,152","#0d12b5","264,166","#e60012","216,260","#ffffff","316,268","#ffffff","645,262","#ffffff","744,266","#ffffff"],
        "shared_detection": True,
        "priority": 1,
        "cooldown": 999.0,
        "sleep": 3,
    },
           {
        "task_name": "Click [Update] When Game Updated!",
        "type": "pixel",
        "click_location_str": "619,374",
        "search_array": ["248,152","#0d12b5","278,166","#e60012","385,152","#191925","574,155","#191925","683,375","#2059f9"],
        "shared_detection": True,
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 3,
    },
    
    # HIGH PRIORITY - UI Elements/Popups (Priority 5-10)
    {
        "task_name": "Click [Skip]",
        "type": "template",
        "template_path": "templates/Shared/Skip.png",
        "roi": [830, 1, 129, 59],
        "confidence": 0.70,
        "use_match_position": True,
        
        "shared_detection": True,
        "priority": 5,
        "cooldown": 5.0,  # Prevent skip button spam
    },
    {
        "task_name": "Click [Close] for Hard Mode Unlocked",
        "type": "template",
        "template_path": "templates/Shared/Close.png",
        "roi": [326, 340, 302, 55],
        "confidence": 0.90,
        "use_match_position": True,
        
        "shared_detection": True,
        "priority": 8,
        "cooldown": 5.0,
        "StopSupport": "json_Character_Slots_Purchased",
    },
    
    # MEDIUM PRIORITY - Store/Purchase Actions (Priority 40-50)
    {
        "task_name": "Go To Purchase Tickets",
        "type": "template",
        "template_path": "templates/Purchase_Tickets/PurchaseTickets.png",
        "roi": [390, 341, 169, 55],
        "confidence": 0.90,
        "use_match_position": True,
        
        "priority": 40,
        "cooldown": 5.0,
    },
    {
        "task_name": "Click 25 Tickets",
        "type": "template",
        "template_path": "templates/Purchase_Tickets/25Tickets.png",
        "roi": [194, 319, 564, 129],
        "confidence": 0.90,
        "use_match_position": True,
        
        "priority": 45,
        "cooldown": 5.0,
    },
    {
        "task_name": "Confirm Ticket Purchase",
        "type": "template",
        "template_path": "templates/Purchase_Tickets/Purchase.png",
        "roi": [534, 343, 174, 56],
        "confidence": 0.90,
        "use_match_position": True,
        
        "priority": 45,
        "cooldown": 5.0,
    },

        {
        "task_name": "Click [Prepare To Battle]",
        "type": "pixel",
        "click_location_str": "693,492",
        "search_array": ["527,486","#0c3be2","567,490","#ffffff","660,493","#ffffff","754,492","#ffffff"],
        
        "priority": 5,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Click [Start Quest]",
        "type": "pixel",
        "click_location_str": "715,497",
        "search_array": ["583,490","#ffffff","652,491","#0d3de4","671,498","#ffffff","735,496","#ffffff"],
        
        "priority": 20,
        "cooldown": 5.0,
        "StopSupport": "json_Character_Slots_Purchased",
        "sleep": 3,
    },

     {
        "task_name": "Click New Record Word To Open Next Quest Menu",
        "type": "pixel",
        "click_location_str": "449,503",
        "search_array": ["833,35","#ff0000","819,54","#ffffff","834,74","#ff0000"],
        
        "priority": 20,
        "sleep": 3,
    },
    {
        "task_name": "Click [Next Quest]",
        "type": "pixel",
        "click_location_str": "756,508",
        "search_array": ["713,512","#ffffff","760,507","#ffffff","698,496","#1e46f2"],
        
        "priority": 20,
        "sleep": 3,
    },
    {
        "task_name": "New Record Quest Obtained",
        "type": "pixel",
        "click_location_str": "478,281",
        "search_array": ["170,273","#fefefe","810,187","#ff0000","798,209","#ffffff"],
        
        "priority": 20,
        "sleep": 3,
    },
        {
        "task_name": "New Record Quest Obtained",
        "type": "pixel",
        "click_location_str": "469,504",
        "search_array": ["183,77","#ffffff","398,503","#ffffff","567,508","#ffffff","339,428","#1f9bf4"],
        
        "priority": 20,
        "sleep": 3,
    },
        # Social/Cancel Actions - Lower Priority
    {
        "task_name": "Click [Cancel] For Friend Request",
        "type": "pixel",
        "click_location_str": "344,409",
        "search_array": ["720,121","#0d12b5","713,134","#e60012","489,175","#ffffff","565,174","#ffffff"],
        
        "priority": 50,
        "sleep": 3,
    },

    # Map Already Clear But Trying to Re Read
    {
        "task_name": "Click [Cancel] For Re-Read Map",
        "type": "pixel",
        "click_location_str": "343,374",
        "search_array": ["249,153","#0d12b5","259,163","#e60012","535,262","#ffffff","612,263","#ffffff","542,258","#ffffff"],
        
        "priority": 20,
        "sleep": 3,
    },
        {
        "task_name": "Sinkaemon Event Unlocked Click [Close]",
        "type": "pixel",
        "click_location_str": "344,481",
        "search_array": ["318,49","#191919","384,50","#191919","454,46","#191919","652,49","#191919","738,45","#0d12b5","727,58","#e60012"],
        
        "priority": 20,
        "sleep": 3,
    },
]