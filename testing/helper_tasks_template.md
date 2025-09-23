I need to add a helper task set called [HELPER_NAME] that will:
1. Be triggered when [TRIGGER_CONDITION]
2. Perform [HELPER_ACTIONS]
3. Return to [RETURN_TASK_SET] when done

This is a temporary helper that should NOT:
- Track state in device JSON
- Have json_ flags
- Be part of the main progression

Please:
1. Create the helper task array
2. Add task mapping in background_process.py
3. Add trigger flag from calling task
4. Add return flag to go back