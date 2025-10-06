# Time-Limited Search Implementation

## Summary
This implementation adds a time-limited search feature for the "Swipe If The Password/Email is Remembered [KLAB Login]" task. The task will only search for the swipe target for 5 seconds after the Password_Complete flag is set, then automatically continue with the rest of the login flow.

## Changes Made

### 1. Task Configuration (login2_klab_login_tasks.py)
✅ Added `"TimeLimitedSearch": 5` to the swipe task, which means:
- The task will start searching when `Password_Complete` flag is set
- It will search for up to 5 seconds
- If found within 5 seconds, it executes the swipe
- If not found within 5 seconds, it sets `Remembered_Check_Complete` flag and continues

### 2. Background Process Logic (background_process.py)

#### Added to OptimizedBackgroundMonitor.__init__:
```python
self.time_limited_search_start: Dict[str, float] = {}  # Track when time-limited search started
self.time_limited_search_flags: Dict[str, Set[str]] = defaultdict(set)  # Track which flags triggered time-limited search
```

#### Modified ProcessMonitor.should_skip_task():
- Added logic to handle `TimeLimitedSearch` parameter
- Starts a timer when the required flag is first set
- Allows the task to run for the specified time limit
- After timeout, skips the task and sets completion flag

## How It Works

1. **Password Entry**: When password is entered, `Password_Complete` flag is set to 1
2. **Timer Starts**: The swipe task sees the flag and starts a 5-second timer
3. **Search Phase**: For 5 seconds, the system searches for the swipe template
4. **Two Outcomes**:
   - **Found**: If template is found, swipe is executed, `Remembered_Check_Complete` is set
   - **Timeout**: After 5 seconds, `Remembered_Check_Complete` is set automatically, task is skipped
5. **Continue**: Cloudflare task proceeds normally (only requires `Password_Complete`)

## Manual Changes Still Needed

To complete the implementation, you need to add the time-limited search state clearing to the ProcessMonitor's `reset_action_tracking` method (line 109):

```python
def reset_action_tracking(self, device_id: str):
    """Reset action tracking for a device"""
    self.last_action_time[device_id] = time.time()
    self.action_count[device_id] = {}
    self.last_action_name[device_id] = None
    
    # Clear time-limited search state from OptimizedBackgroundMonitor if it exists
    from background_process import monitor
    if hasattr(monitor, 'time_limited_search_start') and device_id in monitor.time_limited_search_start:
        del monitor.time_limited_search_start[device_id]
    if hasattr(monitor, 'time_limited_search_flags') and device_id in monitor.time_limited_search_flags:
        monitor.time_limited_search_flags[device_id].clear()
```

This ensures that when task sets are switched or the device restarts, the time-limited search state is properly cleared.

## Benefits
- No dummy tasks needed
- Clean implementation using existing flag system
- Automatic timeout prevents getting stuck
- Other tasks proceed normally after timeout
- Maintains the step-by-step flow: Email → Password → (Optional Swipe) → Cloudflare → Login

## Testing
To test this implementation:
1. Run the login flow
2. After password is entered, watch the logs for "⏱️ Starting 5s time-limited search"
3. If swipe template exists, it should be found and executed
4. If not found, after 5 seconds you should see "⏱️ Time limit (5s) expired"
5. Cloudflare button should be clicked next in both cases
