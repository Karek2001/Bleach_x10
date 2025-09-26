Recive_Giftbox_Check = [

    {
        "task_name": "From [Gifts] To [Soul Tickets]",
        "type": "pixel",
        "click_location_str": "382,79",
        "search_array": ["189,87","#464ac6","324,80","#616060"],
        
        "priority": 25,
        "cooldown": 5.0,
        "Recive_GiftBox_Tasks": True,
        "sleep": 3,
    },
        {
        "task_name": "From [Soul Tickets] To [Characters]",
        "type": "pixel",
        "click_location_str": "568,82",
        "search_array": ["321,81","#6365ce","503,80","#616060"],
        
        "priority": 25,
        "cooldown": 5.0,
        "Recive_GiftBox_Tasks": True,
        "sleep": 3,
    },
        {
        "task_name": "From [Characters] To [Friend Points]",
        "type": "pixel",
        "click_location_str": "743,79",
        "search_array": ["500,81","#6365ce","670,80","#616060"],
        
        "priority": 25,
        "cooldown": 5.0,
        "Recive_GiftBox_Tasks": True,
        "sleep": 3,
    },

            {
        "task_name": "All Gifts Are Recived No More To Recive",
        "type": "pixel",
        "click_location_str": "486,487",
        "search_array": ["462,72","#727171","461,72","#727171","638,72","#727171","812,72","#8789d9"],
        
        "priority": 1,
        "cooldown": 5.0,
        "ConditionalRun": ["Skip_Kon_Bonaza"],
        "json_Recive_GiftBox":True,
        "Skip_Yukio_Event_Tasks": True,
 "Reset_Yukio_Retry": True,
        "sleep": 3,
    },
            {
        "task_name": "All Gifts Are Recived No More To Recive But Kon Event Isn't Finished Yet",
        "type": "pixel",
        "click_location_str": "484,486",
        "search_array": ["462,72","#727171","461,72","#727171","638,72","#727171","812,72","#8789d9"],
        
        "priority": 1,
        "cooldown": 5.0,
        "StopSupport": "json_Kon_Bonaza",
        # HERE RETURN TO KON IF IT DOESN't TRUE
        "Skip_Kon_Bonaza_Tasks": True,
        "sleep": 3,
    },

]