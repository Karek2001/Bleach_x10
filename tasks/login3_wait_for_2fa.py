# login3_wait_for_2fa.py - 2FA Wait Helper Tasks
"""
Helper tasks for waiting and handling 2FA authentication.
Called from login2_klab_login_tasks.
"""

Login3_Wait_For_2FA_Tasks = [
    {
        "task_name": "Detect 2FA Code Request [Wait for 2FA]",
        "type": "pixel",
        "click_location_str": "0,0",  # Detection only
        "search_array": ["246,377","#23aabc","239,376","#edf1f2"],  # 2FA screen
        "priority": 1,
        "cooldown": 5.0,
        "shared_detection": True,
        "min_matches_for_swipe": 1,
        "swipe_command": "shell input swipe 443 400 443 140 900",
        "sleep": 2.0
    },
    {
        "task_name": "Enter 2FA Code [Wait for 2FA]",
        "type": "template",
        "template_path": "templates/Login/VerificationCode.png",
        "roi": [283, 222, 382, 137],
        "priority": 5,
        "cooldown": 3.0,
        "sleep": 2.0,
        "Confirm_2FA_Code_Tasks": True,
        "Get_2fa": True,
    },
]
