SubStories_check = [

        {
        "task_name": "Not All Sub-Storiies sheet are clear",
        "type": "Pixel-OneOrMoreMatched",
        "pixel-values":["175,115","#ff4866","175,200","#ff4866","175,285","#ff4866","175,371","#ff4866","406,115","#ff4866","405,200","#ff4866","405,285","#ff4866","406,371","#ff4866","630,115","#ff4866","630,200","#ff4866","630,285","#ff4866","611,370","#ff4866"],
        "click_location_str": "0,0",
        "priority": 1,
        "KeepChecking": 5.0,
        "cooldown": 5.0,
        "Sub-Stores": True
    },

        # 5 Pages ONLY WORKS
            {
        "task_name": "From Page 1 To Page 2 [5 Pages ONLY WORKS]",
        "type": "pixel",
        "search_array": ["338,488","#ec4d01","420,486","#3f4b58"],
        "click_location_str": "400,483",
        "priority": 20,
        "cooldown": 5.0,
        "Sub-Stores": True
    },
                {
        "task_name": "From Page 2 To Page 3 [5 Pages ONLY WORKS]",
        "type": "pixel",
        "search_array": ["420,488","#ec4d01","501,486","#3f4b58"],
        "click_location_str": "481,482",
        "priority": 21,
        "cooldown": 5.0,
        "Sub-Stores": True
    },
                    {
        "task_name": "From Page 3 To Page 4 [5 Pages ONLY WORKS]",
        "type": "pixel",
        "search_array": ["500,488","#ec4d01","663,486","#3f4b58"],
        "click_location_str": "562,484",
        "priority": 22,
        "cooldown": 5.0,
        "Sub-Stores": True
    },
                        {
        "task_name": "From Page 4 To Page 5 [5 Pages ONLY WORKS]",
        "type": "pixel",
        "search_array": ["578,488","#ec4d01","663,486","#3f4b58"],
        "click_location_str": "643,483",
        "priority": 23,
        "cooldown": 5.0,
        "Sub-Stores": True
    },
                        {
        "task_name": "Last Page No Pages Left [5 Pages ONLY WORKS]",
        "type": "Pixel-OneOrMoreMatched",
        "pixel-values":["662,488","#ec4d01","578,488","#ec4d01","500,488","#ec4d01","420,488","#ec4d01"],
        "click_location_str": "25,21",
        "priority": 25,
        "KeepChecking": 5.0,
        "cooldown": 5.0,
        "Sub-Stores": True
    }
,
    # Works Only in 4 Pages
            # 5 Pages ONLY WORKS
            {
        "task_name": "From Page 1 To Page 2 [4 Pages ONLY WORKS]",
        "type": "pixel",
        "search_array": ["379,488","#ec4d01","460,486","#3f4b59"],
        "click_location_str": "441,483",
        "priority": 20,
        "cooldown": 5.0,
        "Sub-Stores": True
    },
                {
        "task_name": "From Page 2 To Page 3 [4 Pages ONLY WORKS]",
        "type": "pixel",
        "search_array": ["460,488","#ec4d01","541,486","#3f4b59"],
        "click_location_str": "521,483",
        "priority": 21,
        "cooldown": 5.0,
        "Sub-Stores": True
    },
                    {
        "task_name": "From Page 3 To Page 4 [4 Pages ONLY WORKS]",
        "type": "pixel",
        "search_array": ["539,488","#ec4d01","604,487","#ffffff"],
        "click_location_str": "602,485",
        "priority": 22,
        "cooldown": 5.0,
        "Sub-Stores": True
    },
                        {
        "task_name": "Last Page No Pages Left [4 Pages ONLY WORKS]",
        "type": "pixel",
        "search_array":["620,488","#ec4d01"],
        "click_location_str": "24,21",
        "priority": 25,
        "KeepChecking": 5.0,
        "cooldown": 5.0,
        "Sub-Stores": True
    },
    # Works Only in 2 Pages
            {
        "task_name": "From Page 1 To Page 2 [2 Pages ONLY WORKS]",
        "type": "pixel",
        "search_array": ["459,488","#ec4d01","523,491","#ffffff"],
        "click_location_str": "521,482",
        "priority": 20,
        "cooldown": 5.0,
        "Sub-Stores": True
    },
                        {
        "task_name": "Last Page No Pages Left [2 Pages ONLY WORKS]",
        "type": "pixel",
        "search_array":["539,489","#ee5001"],
        "click_location_str": "24,21",
        "priority": 25,
        "KeepChecking": 5.0,
        "cooldown": 5.0,
        "Sub-Stores": True
    },
]