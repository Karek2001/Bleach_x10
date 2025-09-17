from .detect_chapter_end import DETECT_CHAPTER_END

StoryMode_Tasks = [

        # LOWER PRIORITY - Navigation/Menu Access (Priority 35-40)
    {
        "task_name": "Open [SOLO] Menu For Story Mode",
        "type": "template",
        "template_path": "templates/Restarting/Solo.png",
        "roi": [814, 420, 142, 118],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "priority": 35,
        "cooldown": 5.0,
    },

            {
        "task_name": "Open Story Window",
        "type": "pixel",
        "click_location_str": "531,193",
        "search_array": ["479,146","#ebebea","457,184","#ffffff","524,191","#ffffff"],
        "isLogical": False,
        "StopSupport": "json_SideMode",
        "sleep": 3,
    },

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
        "cooldown": 5.0,
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
        "cooldown": 5.0,
        "StopSupport": "json_SideMode",
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
        "isLogical": False,
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
        "isLogical": False,
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
        "isLogical": False,
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
        "isLogical": False,
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
