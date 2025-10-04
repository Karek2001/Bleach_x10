from .detect_chapter_end import DETECT_CHAPTER_END

StoryMode_Tasks = [
    {
        "task_name": "Click [Close] Opened Window Setting Wrongly",
        "type": "pixel",
        "click_location_str": "481,491",
        "search_array": ["442,36","#191919""174,149","#29fe21","166,75","#ffffff","640,223","#ff0004","452,486","#ffffff"],
        "priority": 5,
        "cooldown": 99.0,
        "sleep": 3,
    },
    {
        "task_name": "Currently Story Mode Is Completed! Lets Return To [HOME]",
        "type": "pixel",
        "click_location_str": "478,368",
        "search_array": ["247,151","#0d12b5","257,164","#e60012","395,156","#191925","566,155","#191925","576,153","#191925","699,279","#ffffff"],
        "priority": 1,
        "cooldown": 10.0,
        "sleep": 3,
        "delayed_click_location": "390,508",
        "delayed_click_delay": 3.0,
    },
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
        "task_name": "Click [Next Quest] [Story Mode]",
        "type": "pixel",
        "click_location_str": "756,508",
        "search_array": ["713,512","#ffffff","760,507","#ffffff","698,496","#1e46f2"],
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },

        # LOWER PRIORITY - Navigation/Menu Access (Priority 35-40)
    {
        "task_name": "Open [SOLO] Menu For Story Mode",
        "type": "pixel",
        "click_location_str": "895,493",
        "search_array": ["885,490","#211d15","899,495","#211d15","906,485","#978e74","892,493","#978e74"],
        "priority": 1,
        "cooldown": 30.0,
        "sleep": 3
    },

            {
        "task_name": "Open Story Window",
        "type": "pixel",
        "click_location_str": "531,193",
        "search_array": ["479,146","#ebebea","457,184","#ffffff","524,191","#ffffff"],
        "StopSupport": "json_SideMode",
        "sleep": 3,
        "priority": 1,
        "cooldown": 30.0,
        "sleep": 3
    },

    {
        "task_name": "Click Story MAP",
        "type": "template",
        "template_path": "templates/Story_Mode/StoryMAP.png",
        "roi": [3, 127, 956, 347],
        "confidence": 0.80,  # Increased from 0.75 to prevent false positives
        "use_match_position": True,
        "shared_detection": True,
        "multi_click": True,  # Click all detected story map icons
        "priority": 5,
        "cooldown": 5.0,
        "sleep": 3
    },

        {
        "task_name": "All Posibile Ways of Stars Map #1",
        "type": "template",
        "template_path": "templates/Story_Mode/Stars.png",
        "roi": [3, 86, 953, 415],
        "confidence": 0.70,
        "use_match_position": True,
        "FullyAnylaze": True,
        "isLogical": False,
        "shared_detection": True,
        "multi_click": True,  # Click all stars found
        "priority": 20,
        "cooldown": 5.0,
        "StopSupport": "json_SideMode",
    },
    # Battle Preparation - Medium Priority

    
    # Quest Progression
    {
        "task_name": "Click White Tap Button",
        "type": "pixel",
        "click_location_str": "665,507",
        "search_array": ["917,13","#0e2988","671,500","#4e4e67"],
        
        "priority": 35,
        "cooldown": 5.0,  # Short cooldown for tap-to-continue
        "StopSupport": "json_SideMode",
        "sleep": 3,
    },
   

    
    # Chapter Navigation
    {
        "task_name": "Click Arrow If All Chapters Clear",
        "type": "template",
        "template_path": "templates/Story_Mode/NextStories.png",
        "roi": [856, 206, 102, 107],
        "confidence": 0.55,
        "use_match_position": True,
        
        "priority": 1,
        "cooldown": 5.0,
        "sleep": 8.5,
        "StopSupport": "json_SideMode",
    },
    
    # Uncleared Content Selection
    # Uncleared Content Selection
    {
        "task_name": "Choose Uncleared Part",
        "type": "template",
        "template_path": "templates/Story_Mode/UnClearedPart.png",
        "roi": [5, 223, 952, 164],
        "confidence": 0.90,
        "use_match_position": True,
        
        "priority": 25,
        "cooldown": 5.0,
        "StopSupport": "json_SideMode",
    },
        {
        "task_name": "Choose Uncleared Part",
        "type": "template",
        "template_path": "templates/Story_Mode/UnClearedPart2.png",
        "roi": [5, 223, 952, 164],
        "confidence": 0.90,
        "use_match_position": True,
        
        "shared_detection": True,
        "priority": 25,
        "cooldown": 5.0,
        "StopSupport": "json_SideMode",
    },
        # HARD MODE SWITCHER (STORY MODE FINISHED)
            {
        "task_name": "Part 21 Finished Detected",
        "type": "template",
        "template_path": "templates/Story_Mode/Part21_full.png",
        "roi": [308, 61, 648, 389],
        "confidence": 0.90,
        
        "HardStory": True,  # Switches to HardStory_tasks
        "priority": 5,  # <-- ADD THIS LINE
    },
            {
        "task_name": "Part 21 Finished Detected [Pixels]",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["458,361","#ffff00","353,102","#009aff","373,274","#191925","424,269","#191925","434,273","#191925","480,360","#ffff00","506,364","#e9e902"],
        
        "HardStory": True,  # Switches to HardStory_tasks
        "priority": 5,  # <-- ADD THIS LINE,
    },
        {
        "task_name": "Click [Start Quest] [This Because Last Stuck Brokes Side Story Isn't Completed]",
        "type": "pixel",
        "click_location_str": "715,497",
        "search_array": ["583,490","#ffffff","652,491","#0d3de4","671,498","#ffffff","735,496","#ffffff"],
        "shared_detection": True,
        "priority": 20,
        "cooldown": 5.0,
        "sleep": 3,
    },

] +  DETECT_CHAPTER_END
