I need to add a new main task set called [TASK_NAME] that will:
1. Be part of the sequential progression after [PREVIOUS_TASK]
2. Track completion in device state as [STATE_KEY_NAME]
3. Move to [NEXT_TASK] when complete

The task should:
- Detect: [WHAT TO DETECT]
- Action: [WHAT TO CLICK/DO]
- Complete when: [COMPLETION CONDITION]

Please:
1. Create the task array with json_[STATE_KEY] flag
2. Add state tracking to device_state_manager.py
3. Update task progression logic
4. Add task switching flags
5. Import the task properly