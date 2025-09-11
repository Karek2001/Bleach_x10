# tasks/restarting_tasks.py - Complete tasks for game startup and initial navigation

Restarting_Tasks = [
# Click White Screen of Klab Company So when it spams 10 Times that Means game freezed
    {
        "task_name": "Game Opened Ready To Use",
        "type": "pixel",
        "click_location_str": "0,0",
        "search_array": ["894,485","#978e74","497,524","#ffffff","790,16","#593b0d","873,190","#ffffff"],
        "BackToStory": True,  # Use normal progression logic like when game is running
        "priority": 1,
        "cooldown": 60.0,
    },
    {
        "task_name": "Bleach isn't Responsing",
        "type": "pixel",
        "click_location_str": "364,292",
        "search_array": ["244,218","#191c1e","239,289","#00658c","211,198","#f0f1f3"],
        "isLogical": False,
        "priority": 1,
        "cooldown": 1.0,
    },
    {
        "task_name": "Click Klab Logo To Restart Game",
        "type": "pixel",
        "click_location_str": "490,276",
        "search_array": ["367,275","#005ead","444,296","#e95293","448,244","#005ead","588,249","#005ead"],
        "isLogical": False,
        "priority": 1,
        "cooldown": 5.0,
    },

    # HIGHEST PRIORITY - Error Recovery/Back Navigation (Priority 5-10)
    {
        "task_name": "Click[Back] In Selling Character Window",
        "type": "pixel",
        "click_location_str": "23,22",
        "search_array": ["216,512","#e24601","74,26","#ffffff","24,21","#ffffff","53,27","#ffffff"],
        "isLogical": False,
        "priority": 5,
        "cooldown": 5.0,
    },
    
    # HIGH PRIORITY - Game Start/Mod Menu (Priority 10-15)
    {
        "task_name": "Click [Thank You] For Mod Menu",
        "type": "pixel",
        "click_location_str": "434,470",
        "search_array": ["265,470","#1c262b","338,469","#ffffff"],
        "isLogical": False,
        "priority": 10,
        "cooldown": 5.0,
    },
    {
        "task_name": "Click [Game Start]",
        "type": "pixel",
        "click_location_str": "477,452",
        "search_array": ["880,490","#515151","937,512","#e60012"],
        "isLogical": False,
        "priority": 15,
        "cooldown": 5.0,
    },
    {
        "task_name": "Click [Game Start 2]",
        "type": "pixel",
        "click_location_str": "471,450",
        "search_array": ["845,505","#fdfdfd","856,513","#e81828","14,21","#ffffff"],
        "isLogical": False,
        "priority": 15,
        "cooldown": 5.0,
    },
    
    # MEDIUM PRIORITY - Quest/Event Handling (Priority 20-30)
    {
        "task_name": "Click [Yes] For Paused Quest Error",
        "type":"pixel",
        "click_location_str": "619,373",
        "search_array": ["251,153","#0d12b5","260,165","#e60012","432,151","#191925","239,224","#ffffff","368,227","#ffffff"],
        "isLogical": False,
        "priority": 20,
        "cooldown": 5.0,
    },
       {
        "task_name": "Click [No] For Continue Playing Quest",
        "type":"pixel",
        "click_location_str": "345,374",
        "search_array": ["246,154","#0d12b5","262,164","#e60012","430,276","#ffffff","471,275","#ffffff","496,275","#ffffff"],
        "isLogical": False,
        "priority": 20,
        "cooldown": 5.0,
    },
    {
        "task_name": "Exit News",
        "type": "template",
        "template_path": "templates/Restarting/Exit.png",
        "roi": [731, 0, 228, 133],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "shared_detection": True,
        "priority": 25,
        "cooldown": 5.0,
    },
    

    
    # LOW PRIORITY - Login Bonuses (Priority 40-50)
    {
        "task_name": "Login Bonus Begginer",
        "type": "pixel",
        "click_location_str": "534,338",
        "search_array": ["195,93","#e50012","182,82","#0d12b4","334,79","#191925"],
        "isLogical": False,
        "priority": 40,
        "cooldown": 5.0,
    },
    {
        "task_name": "Login Bonus",
        "type": "pixel",
        "click_location_str": "626,510",
        "search_array": ["405,36","#191925","483,36","#191925","255,47","#e50012","255,35","#0d12b4"],
        "isLogical": False,
        "priority": 40,
        "cooldown": 5.0,
    },
    {
        "task_name": "Skip Any New Events/Windows Opened By Clicking [OK]",
        "type": "template",
        "template_path": "templates/Restarting/OK.png",
        "roi": [2, 285, 559, 244],
        "confidence": 0.90,
        "use_match_position": True,
        "isLogical": False,
        "shared_detection": True,  # Check with other UI elements
        "priority": 50,
        "cooldown": 5.0,
    },
]