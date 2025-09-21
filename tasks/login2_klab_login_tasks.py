
Login2_Klab_Login_Tasks = [
    # STEP 1: Email Task (runs first, then delays other tasks)
    {
        "task_name": "Click [Email TextBox] [KLAB Login]",
        "type": "template",
        "template_path": "templates/Login/Email.png",
        "roi": [267, 106, 130, 158],
        "confidence": 0.80,
        "use_match_position": True,
        "DownPixels": 35,
        "priority": 1,
        "cooldown": 999.0,  # Never runs again
        "sleep": 3,
        "Enter_Email": True
    },
    
    # STEP 2: Password Task (delayed start, then runs once)
    {
        "task_name": "Click [Password TextBox] [KLAB Login]",
        "type": "template",
        "template_path": "templates/Login/Password.png",
        "roi": [274, 213, 210, 239],
        "confidence": 0.80,
        "use_match_position": True,
        "DownPixels": 35,
        "priority": 2,
        "cooldown": 10.0,  # Starts checking after email cooldown
        "sleep": 3.0,
        "Enter_Password": True
    },
    
    # STEP 3: Cloudflare Task (lower priority, runs after password)  
    {
        "task_name": "Click [Cloudflare Button] [KLAB Login]",
        "type": "template",
        "template_path": "templates/Login/CloudFlareButton.png",
        "roi": [264, 328, 169, 184],
        "confidence": 0.90,
        "use_match_position": True,
        "priority": 3,
        "cooldown": 5.0,
        "sleep": 3.0
    },
    
    # STEP 4: Login Button (lowest priority, runs last)
    {
        "task_name": "Click [Login Button] [KLAB Login]",
        "type": "template",
        "template_path": "templates/Login/sucessCloudFlare.png",
        "roi": [264, 328, 169, 184],
        "confidence": 0.90,
        "use_match_position": True,
        "DownPixels": 103,
        "priority": 4,
        "cooldown": 10.0,
        "sleep": 2.0,
        "Login3_Wait_For_2FA_Tasks": True  # Trigger next task set
    },

]
