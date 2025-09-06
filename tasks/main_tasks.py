from .detect_chapter_end import DETECT_CHAPTER_END

Main_Tasks = [
    {
        "task_name": "Click Story MAP",
        "type": "template",
        "template_path": "templates/Story_Mode/StoryMAP.png",
        "roi": [3, 127, 956, 347],
        "confidence": 0.80,  # Increased from 0.75 to prevent false positives
        "use_match_position": True,
        "isLogical": False,
        "shared_detection": True,
        "priority": 30,
        "cooldown": 2.0,
    },
        {
        "task_name": "Click feetMap",
        "type": "template",
        "template_path": "templates/Story_Mode/feetMap.png",
        "roi": [3, 127, 956, 347],
        "confidence": 0.60,  # Increased from 0.75 to prevent false positives
        "use_match_position": True,
        "isLogical": False,
        "shared_detection": True,
        "priority": 30,
        "cooldown": 2.0,
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
        "cooldown": 3.0,
    },
    
    # Battle Preparation - Medium Priority
    {
        "task_name": "Click [Prepare To Battle]",
        "type": "pixel",
        "click_location_str": "693,492",
        "search_array": ["527,486","#0c3be2","567,490","#ffffff","660,493","#ffffff","754,492","#ffffff"],
        "isLogical": False,
        "priority": 5,
        "cooldown": 2.0,
    },
    {
        "task_name": "Click [Start Quest]",
        "type": "pixel",
        "click_location_str": "715,497",
        "search_array": ["583,490","#ffffff","652,491","#0d3de4","671,498","#ffffff","735,496","#ffffff"],
        "isLogical": False,
        "priority": 5,
        "cooldown": 2.0,
    },
    
    # Quest Progression
    {
        "task_name": "Click White Tap Button",
        "type": "pixel",
        "click_location_str": "665,507",
        "search_array": ["917,13","#0e2988","671,500","#4e4e67"],
        "isLogical": False,
        "priority": 35,
        "cooldown": 0.5,  # Short cooldown for tap-to-continue
    },
    {
        "task_name": "Click New Record Word To Open Next Quest Menu",
        "type": "pixel",
        "click_location_str": "449,503",
        "search_array": ["833,35","#ff0000","819,54","#ffffff","834,74","#ff0000"],
        "isLogical": False,
        "priority": 20,
    },
    {
        "task_name": "Click [Next Quest]",
        "type": "pixel",
        "click_location_str": "756,508",
        "search_array": ["713,512","#ffffff","760,507","#ffffff","698,496","#1e46f2"],
        "isLogical": False,
        "priority": 5,
    },
    {
        "task_name": "New Record Quest Obtained",
        "type": "pixel",
        "click_location_str": "478,281",
        "search_array": ["170,273","#fefefe","810,187","#ff0000","798,209","#ffffff"],
        "isLogical": False,
        "priority": 20,
    },
    
    # Social/Cancel Actions - Lower Priority
    {
        "task_name": "Click [Cancel] For Friend Request",
        "type": "pixel",
        "click_location_str": "344,409",
        "search_array": ["720,121","#0d12b5","713,134","#e60012","489,175","#ffffff","565,174","#ffffff"],
        "isLogical": False,
        "priority": 50,
    },
    # Story Already Clear But Trying to Re Read
    {
        "task_name": "Click [Cancel] For Re-Read Story",
        "type": "pixel",
        "click_location_str": "343,374",
        "search_array": ["249,153","#0d12b5","259,163","#e60012","535,262","#ffffff","612,263","#ffffff","542,258","#ffffff"],
        "isLogical": False,
        "priority": 20,
    },
    
    # Chapter Navigation
    {
        "task_name": "Click Arrow If All Chapters Clear",
        "type": "template",
        "template_path": "templates/Story_Mode/NextStories.png",
        "roi": [856, 206, 102, 107],
        "confidence": 0.55,
        "use_match_position": True,
        "isLogical": False,
        "shared_detection": True,
        "priority": 1,
        "cooldown": 3.0,
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
        "isLogical": False,
        "priority": 25,
        "cooldown": 2.0,
    },
        {
        "task_name": "Choose Uncleared Part",
        "type": "template",
        "template_path": "templates/Story_Mode/UnClearedPart2.png",
        "roi": [5, 223, 952, 164],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "shared_detection": True,
        "priority": 25,
        "cooldown": 2.0,
    },
        # HARD MODE SWITCHER (STORY MODE FINISHED)
            {
        "task_name": "Part 21 Finished Detected",
        "type": "template",
        "template_path": "templates/Story_Mode/Part21_full.png",
        "roi": [308, 61, 648, 389],
        "confidence": 0.90,
        "isLogical": False,
        "HardStory": True,  # Switches to HardStory_tasks
        "priority": 5,  # <-- ADD THIS LINE
    },
            {
        "task_name": "Part 21 Finished Detected [Pixels]",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["458,361","#ffff00","353,102","#009aff","373,274","#191925","424,269","#191925","434,273","#191925","480,360","#ffff00","506,364","#e9e902"],
        "isLogical": False,
        "HardStory": True,  # Switches to HardStory_tasks
        "priority": 5,  # <-- ADD THIS LINE,
    },


] +  DETECT_CHAPTER_END
