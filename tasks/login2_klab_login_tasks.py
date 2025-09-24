
Login2_Klab_Login_Tasks = [
    # STEP 1: Email Task (runs first, sets completion flag)
    {
        "task_name": "Click [Email TextBox] [KLAB Login]",
        "type": "template",
        "template_path": "templates/Login/Email.png",
        "roi": [267, 106, 130, 158],
        "confidence": 0.80,
        "use_match_position": True,
        "DownPixels": 35,
        "priority": 1,
        "cooldown": 999.0,  # Never runs again after completion
        "sleep": 4,
        "Enter_Email": True,
        "SetFlag_Email_Complete": True  # Mark email step as complete
    },
    
    # STEP 2: Password Task (runs only after email is complete)
    {
        "task_name": "Click [Password TextBox] [KLAB Login]",
        "type": "template", 
        "template_path": "templates/Login/Password.png",
        "roi": [274, 213, 210, 239],
        "confidence": 0.60,  # Lower confidence to help with detection
        "use_match_position": True,
        "DownPixels": 35,
        "priority": 2,
        "cooldown": 999.0,  # Never runs again after completion
        "sleep": 6,  # Increased sleep to give more time for field to be ready
        "Enter_Password": True,
        "RequireFlag_Email_Complete": True,  # Only run if email is complete
        "SetFlag_Password_Complete": True,  # Mark password step as complete
    },

    {
        "task_name": "Swipe If The Password/Email is Remembered [KLAB Login]",
        "type": "template", 
        "template_path": "templates/Login/needswipe.png",
        "roi": [611, 430, 55, 43],
        "confidence": 0.80,
        "shared_detection": True,
        "min_matches_for_swipe": 1,
        "use_match_position": False,
        "swipe_command": "shell input swipe 443 400 443 140 900",
        "priority": 2.5,  # Run after password (2) but before cloudflare (3)
        "cooldown": 999.0,
        "sleep": 5.0,  # Reduced sleep since it has timeout logic
        "RequireFlag_Password_Complete": True,  # Only run after password is entered
        "SetFlag_Remembered_Check_Complete": True,  # Mark this step as complete
        "TimeLimitedSearch": 5  # Only search for 5 seconds after Password_Complete is set
    },


    
    # STEP 3: Cloudflare Task (runs only after password is complete)
    {
        "task_name": "Click [Cloudflare Button] [KLAB Login]",
        "type": "template",
        "template_path": "templates/Login/CloudFlareButton.png",
        "roi": [232, 109, 566, 350],
        "confidence": 0.90,
        "use_match_position": True,
        "priority": 3,
        "cooldown": 999.0,  # Never runs again after completion
        "sleep": 3.0,
        "RequireFlag_Password_Complete": True,  # Only run if password is complete
        "SetFlag_Cloudflare_Complete": True  # Mark cloudflare step as complete
    },
    
    # STEP 4: Login Button (runs only after cloudflare is complete)
    {
        "task_name": "Click [Login Button] [KLAB Login]",
        "type": "template",
        "template_path": "templates/Login/sucessCloudFlare.png",
        "roi": [232, 109, 566, 350],
        "confidence": 0.90,
        "use_match_position": True,
        "DownPixels": 103,
        "priority": 4,
        "cooldown": 999.0,  # Never runs again after completion
        "sleep": 2.0,
        "RequireFlag_Cloudflare_Complete": True,  # Only run if cloudflare is complete
        "Login3_Wait_For_2FA_Tasks": True  # Trigger next task set
    },

]
