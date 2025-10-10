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
        "cooldown": 5.0,
        "sleep": 3
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
        "sleep": 3
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
        "cooldown": 5.0,
        "sleep": 3
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
        "cooldown": 5.0,
        "sleep": 3
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
        "sleep": 3,
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
        "shared_detection": True,
        "priority": 40,
        "cooldown": 5.0,
        "sleep": 3
    },
    {
        "task_name": "Click 25 Tickets",
        "type": "pixel",
        "click_location_str": "432,385",
        "search_array": ["325,361","#ffffff","341,359","#ffffff","492,371","#ffffff","262,399","#0d3fb7","418,384","#1616f1"],
        "shared_detection": True,
        "priority": 45,
        "cooldown": 5.0,
        "sleep": 3
    },
    {
        "task_name": "Click 50 Tickets",
        "type": "pixel",
        "click_location_str": "500,365",
        "search_array": ["327,352","#ffffff","344,349","#ffffff","401,350","#ffffff","493,354","#ffffff","595,379","#2aff21","255,382","#0e40b9"],
        "shared_detection": True,
        "priority": 45,
        "cooldown": 5.0,
        "sleep": 3
    },

    {
        "task_name": "Confirm Ticket Purchase",
        "type": "pixel",
        "click_location_str": "615,372",
        "search_array": ["246,146","#0d12b5","258,157","#e60012","369,145","#131319","464,149","#131319","582,149","#131319","572,373","#ffffff","668,372","#ffffff"],
        "shared_detection": True,
        "priority": 45,
        "cooldown": 5.0,
        "sleep": 3
    },
        # Tickets Puchased Completed
                               {
        "task_name": "Click [Close] After Purchased Tickets",
        "type": "pixel",
        "click_location_str": "484,373",
        "search_array": ["247,154","#0d12b5","264,165","#e60012","360,152","#191925","591,154","#191925","354,259","#ffffff","606,266","#ffffff","561,252","#ffffff"],
        "priority": 5,
        "cooldown": 10.0,
        "shared_detection": True,
        "sleep": 3,
    },

        {
        "task_name": "Click [Prepare To Battle]",
        "type": "pixel",
        "click_location_str": "693,492",
        "search_array": ["527,486","#0c3be2","567,490","#ffffff","660,493","#ffffff","754,492","#ffffff"],
        
        "shared_detection": True,
        "priority": 5,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Click [Start Quest]",
        "type": "pixel",
        "click_location_str": "715,497",
        "search_array": ["583,490","#ffffff","652,491","#0d3de4","671,498","#ffffff","735,496","#ffffff"],
        
        "shared_detection": True,
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
        
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "New Record Quest Obtained",
        "type": "pixel",
        "click_location_str": "478,281",
        "search_array": ["170,273","#fefefe","810,187","#ff0000","798,209","#ffffff"],
        
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },
        {
        "task_name": "New Record Quest Obtained",
        "type": "pixel",
        "click_location_str": "469,504",
        "search_array": ["183,77","#ffffff","398,503","#ffffff","567,508","#ffffff","339,428","#1f9bf4"],
        
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },
        # Social/Cancel Actions - Lower Priority
    {
        "task_name": "Click [Cancel] For Friend Request",
        "type": "pixel",
        "click_location_str": "344,409",
        "search_array": ["720,121","#0d12b5","713,134","#e60012","489,175","#ffffff","565,174","#ffffff"],
        
        "shared_detection": True,
        "priority": 50,
        "cooldown": 5.0,
        "sleep": 3,
    },

    # Map Already Clear But Trying to Re Read
    {
        "task_name": "Click [Cancel] For Re-Read Map",
        "type": "pixel",
        "click_location_str": "343,374",
        "search_array": ["249,153","#0d12b5","259,163","#e60012","535,262","#ffffff","612,263","#ffffff","542,258","#ffffff"],
        
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },
        {
        "task_name": "Sinkaemon Event Unlocked Click [Close]",
        "type": "pixel",
        "click_location_str": "344,481",
        "search_array": ["318,49","#191919","384,50","#191919","454,46","#191919","652,49","#191919","738,45","#0d12b5","727,58","#e60012"],
        
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },


    # THIS MESSAGE SHOWED UP AFTER FINISHING REROLL SECOND MATCH ASKING USER TO LINK ACCOUNT
            {
        "task_name": "Asking USER TO LINK KLAB ID [Click [CLOSE]]",
        "type": "pixel",
        "click_location_str": "482,494",
        "search_array": ["348,35","#191919","460,39","#191919","479,35","#191919","560,36","#191919","257,51","#e60012","236,83","#ffff00","510,112","#ffff00"],
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },

    # 10x Anniviersry Asking User To Go For Official Website For INFO [Click [CLOSE]]
            {
        "task_name": "10x Anniviersry Asking User To Go For Official Website For INFO [Click [CLOSE]]",
        "type": "pixel",
        "click_location_str": "337,371",
        "search_array": ["258,152","#0d12b5","267,166","#e60012","306,151","#494952","436,154","#191925","473,155","#191925","644,154","#191925","474,262","#ffffff","542,260","#ffffff","539,291","#ffffff"],
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },

    # EVENT INFO ABOUT ICHIGO WITH BASKETBALL [Click [Anywhere]]
                {
        "task_name": "Event Info About Ichigo With Basketball [Click [Anywhere]]",
        "type": "pixel",
        "click_location_str": "812,520",
        "search_array": ["581,56","#302248","597,79","#d9e781","567,42","#343854"],
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },
                   {
        "task_name": "Leave News Window Click [x]",
        "type": "pixel",
        "click_location_str": "931,25",
        "search_array": ["931,25","#ffffff","932,45","#e60012","945,26","#373737"],
        "shared_detection": True,
        "priority": 20,
        "cooldown": 10.0,
        "sleep": 3,
    },

    # SKIP BIGGENER LOGIN BONUS STUFF
                       {
        "task_name": "Login Bonus Anniviersary 10th",
        "type": "pixel",
        "click_location_str": "890,89",
        "search_array": ["181,81","#0d12b3","183,93","#e40012","246,81","#191925","716,86","#191925","521,78","#191925"],
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },
                       {
        "task_name": "Beginner Gifts Login Bonus",
        "type": "pixel",
        "click_location_str": "891,89",
        "search_array": ["334,81","#191925","553,97","#0d12b4","543,126","#e29b48","404,130","#cd7c48","272,124","#2c384c"],
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },
                       {
        "task_name": "Normal Login Bonus",
        "type": "pixel",
        "click_location_str": "857,96",
        "search_array": ["250,34","#0d12b4","266,49","#e50012","404,37","#191925","483,35","#191925","556,39","#191925","559,51","#0d12b4"],
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },

    # SKIP BIRTHDAY CHARACTER 
                           {
        "task_name": "Character Birthday!",
        "type": "pixel",
        "click_location_str": "899,437",
        "search_array": ["846,468","#d27c00","114,468","#d27c00""177,131","#fdc3b1","173,196","#fef89a"],
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },


    
]