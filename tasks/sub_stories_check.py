SubStories_check = [

        {
        "task_name": "Not All Sub-Storiies sheet are clear",
        "type": "Pixel-OneOrMoreMatched",
        "pixel-values":["175,115","#ff4866","175,200","#ff4866","175,285","#ff4866","175,371","#ff4866","406,115","#ff4866","405,200","#ff4866","405,285","#ff4866","406,371","#ff4866","630,115","#ff4866","630,200","#ff4866","630,285","#ff4866","611,370","#ff4866"],
        "click_location_str": "694,189",
        "priority": 1,
        "KeepChecking": 5.0,
        "cooldown": 2.0,
        "Sub-Stores": True
    },

            {
        "task_name": "From Page 1 To Page 2",
        "type": "pixel",
        "search_array": ["338,488","#ec4d01","420,486","#3f4b58"],
        "click_location_str": "400,483",
        "priority": 20,
        "cooldown": 2.0,
        "Sub-Stores": True
    },
                {
        "task_name": "From Page 2 To Page 3",
        "type": "pixel",
        "search_array": ["420,488","#ec4d01","501,486","#3f4b58"],
        "click_location_str": "481,482",
        "priority": 21,
        "cooldown": 2.0,
        "Sub-Stores": True
    },
                    {
        "task_name": "From Page 3 To Page 4",
        "type": "pixel",
        "search_array": ["500,488","#ec4d01","663,486","#3f4b58"],
        "click_location_str": "562,484",
        "priority": 22,
        "cooldown": 2.0,
        "Sub-Stores": True
    },
                        {
        "task_name": "From Page 4 To Page 5",
        "type": "pixel",
        "search_array": ["578,488","#ec4d01","663,486","#3f4b58"],
        "click_location_str": "643,483",
        "priority": 23,
        "cooldown": 2.0,
        "Sub-Stores": True
    },
                        {
        "task_name": "Last Page No Pages Left",
        "type": "Pixel-OneOrMoreMatched",
        "pixel-values":["662,488","#ec4d01","578,488","#ec4d01","500,488","#ec4d01","420,488","#ec4d01"],
        "click_location_str": "25,21",
        "priority": 25,
        "KeepChecking": 5.0,
        "cooldown": 2.0,
        "Sub-Stores": True
    }
]