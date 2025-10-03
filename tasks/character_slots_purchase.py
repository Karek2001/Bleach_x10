# tasks/character_slots_purchase.py - Tasks for purchasing character slots

Character_Slots_Purchase = [
    {
        "task_name": "Detect Game Updated! [Game Update]",
        "type": "pixel",
        "click_location_str": "480,373",
        "search_array": ["249,152","#0d12b5","264,166","#e60012","216,260","#ffffff","316,268","#ffffff","645,262","#ffffff","744,266","#ffffff"],
        "priority": 1,
        "cooldown": 999.0,
        "sleep": 3,
    },
    # Navigate to Shop
    {
        "task_name": "Leave [SOLO] Menu",
        "type": "pixel",
        "click_location_str": "121,220",
        "search_array": ["679,179","#ffffff","736,201","#ffffff","377,201","#fdc46f","175,242","#ffffff","260,109","#ffffff"],
        
        "priority": 10,
        "cooldown": 5.0,
        "sleep": 3,
    },
    {
        "task_name": "Click [Shop]",
        "type": "pixel",
        "click_location_str": "256,503",
        "search_array": ["237,527","#eff1ff","271,527","#eef0ff","275,507","#c7d4c2"],
        
        "priority": 10,
        "cooldown": 5.0,
        "StopSupport":"json_Character_Slots_Purchased",
        "sleep": 3,
    },
        {
        "task_name": "Click [ADS/ITEMS]",
        "type": "pixel",
        "click_location_str": "633,274",
        "search_array": ["608,205","#8a8ca3","652,211","#87899e","641,194","#0c32b8","668,267","#32f533",],
        
        "priority": 10,
        "cooldown": 5.0,
        "StopSupport":"json_Character_Slots_Purchased",
        "sleep": 3,
    },
            {
        "task_name": "Click [Purchase Character Slots]",
        "type": "pixel",
        "click_location_str": "536,86",
        "search_array": ["388,95","#878999","386,116","#e7e7e9","417,85","#ffffff","748,106","#1616f1"],
        
        "priority": 10,
        "cooldown": 5.0,
        "StopSupport":"json_Character_Slots_Purchased",
        "sleep": 3,
    },
                {
        "task_name": "Click [Click Spirit Orbs]",
        "type": "pixel",
        "click_location_str": "681,393",
        "search_array": ["735,120","#0d12b5","712,134","#e60012","753,398","#235cf9","627,396","#ffffff","730,399","#ffffff"],
        
        "priority": 10,
        "cooldown": 5.0,
        "StopSupport":"json_Character_Slots_Purchased",
        "sleep": 3,
    },

                {
        "task_name": "Click [OK] Confirm Purchase",
        "type": "pixel",
        "click_location_str": "623,371",
        "search_array": ["718,144","#0d12b5","706,159","#e60012","369,146","#131319","480,148","#131319","682,376","#225cf9"],
        
        "priority": 10,
        "cooldown": 5.0,
        "StopSupport":"json_Character_Slots_Purchased",
        "Increment_Character_Slots_Count": True,
        "sleep": 3,

    },

                    {
        "task_name": "Back To Main Menu",
        "type": "pixel",
        "click_location_str": "27,26",
        "search_array": ["24,21","#ffffff","24,47","#e60012","5,28","#ffffff","44,15","#080909"],
        
        "priority": 10,
        "cooldown": 5.0,
        "Recive_Gold_From_Box_For_Characters_Purchase_Tasks": True,
        "ConditionalRun": ["Character_Slots_Purchased"],
        "sleep": 3,
    },
]