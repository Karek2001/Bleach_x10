# Task Flags and Keys Documentation

## Overview
This document describes all available flags and keys that can be used in task definitions to control task behavior, detection methods, and game flow.

---

## Detection Type Flags

### `type` (Required)
Specifies the detection method for the task.
- **Values**: `"pixel"`, `"template"`, `"ocr"`, `"Pixel-OneOrMoreMatched"`, `"ConditionalCheck"`
- **Usage**: Determines how the task searches for conditions

### `search_array` 
Used with `type: "pixel"` - Array of coordinate-color pairs to check
- **Format**: `["x,y", "#hexcolor", "x,y", "#hexcolor", ...]`
- **Example**: `["244,218","#191c1e","239,289","#00658c"]`

### `template_path`
Used with `type: "template"` - Path to template image
- **Format**: `"templates/folder/image.png"`
- **Example**: `"templates/Story_Mode/StoryMAP.png"`

### `roi` 
Region of Interest for template matching
- **Format**: `[x, y, width, height]`
- **Example**: `[100, 100, 760, 400]`

### `confidence`
Minimum confidence score for template matching
- **Default**: `0.90`
- **Range**: `0.0 - 1.0`
- **Example**: `0.85`

### `ocr_text`
Text to search for using OCR
- **Format**: Comma-separated list of texts
- **Example**: `"skip,next,continue"`

### `is_id`
Specifies the format for enhanced OCR number extraction
- **Type**: Boolean
- **Values**: 
  - `true` - Extract ID format (e.g., "ID: 88 534 886")
  - `false` - Extract regular numbers (e.g., "21,124")
- **Usage**: Used with enhanced OCR tasks for optimized number detection
- **Example**: `"is_id": false` for currency amounts

### `pixel-values`
Used with `type: "Pixel-OneOrMoreMatched"` - Multiple pixel pairs to check
- **Format**: Array of coordinate-color pairs where any matching pair triggers the task

---

## Click and Position Flags

### `click_location_str`
Coordinates where to click when task is triggered
- **Format**: `"x,y"`
- **Example**: `"480,372"`
- **Special**: `"0,0"` means no click needed

### `use_match_position`
Click at the center of template match instead of fixed location
- **Type**: Boolean
- **Default**: `false`
- **Usage**: Used with template matching to click on found template

### `UpPixels`, `DownPixels`, `LeftPixels`, `RightPixels`
Adjust click position by specified pixels
- **Type**: Integer
- **Example**: `"UpPixels": 10` moves click 10 pixels up

---

## Task Execution Control

### `priority`
Task execution priority (lower = higher priority)
- **Type**: Integer
- **Range**: 1-999
- **Example**: `5` (very high priority)

### `cooldown`
Minimum seconds before task can execute again
- **Type**: Float
- **Default**: `2.0`
- **Example**: `5.0`

### `sleep`
Pause execution after task completes
- **Type**: Float (seconds)
- **Example**: `8.5`

### `KeepChecking`
Continue checking only this task for specified seconds
- **Type**: Float (seconds)
- **Example**: `10.0` keeps checking for 10 seconds

### `shared_detection`
Enable efficient multi-template detection
- **Type**: Boolean
- **Default**: `false`
- **Usage**: Groups templates for single-pass detection

### `multi_click`
Click all instances found (for template matching)
- **Type**: Boolean
- **Default**: `false`
- **Example**: Used for clearing multiple stars on map

### `min_matches_for_swipe`
Minimum number of template matches required to trigger swipe instead of clicks
- **Type**: Integer
- **Usage**: Used with `multi_click` and `swipe_command`
- **Example**: `3` requires 3 matches to trigger swipe

### `swipe_command`
ADB swipe command to execute when match count threshold is met
- **Type**: String
- **Format**: `"shell input swipe x1 y1 x2 y2 duration"`
- **Usage**: Used with `multi_click` and `min_matches_for_swipe`
- **Example**: `"shell input swipe 443 400 443 140 900"`

### `isLogical`
Triggers special logical processing
- **Type**: Boolean
- **Default**: `false`
- **Usage**: Hands control to logical process handler

---

## State Management Flags

### `json_EasyMode`
Sets EasyMode to complete (1) when task is triggered
- **Type**: Boolean flag
- **Sets**: `EasyMode = 1` in device state

### `json_HardMode`
Sets HardMode to complete (1) when task is triggered
- **Type**: Boolean flag
- **Sets**: `HardMode = 1` in device state

### `json_SideMode`
Sets SideMode to complete (1) when task is triggered
- **Type**: Boolean flag
- **Sets**: `SideMode = 1` in device state

### `json_SubStory`
Sets SubStory to complete (1) when task is triggered
- **Type**: Boolean flag
- **Sets**: `SubStory = 1` in device state

### `json_Character_Slots_Purchased`
Sets Character_Slots_Purchased to complete (1)
- **Type**: Boolean flag
- **Sets**: `Character_Slots_Purchased = 1` in device state

### `json_Exchange_Gold_Characters`
Sets Exchange_Gold_Characters to complete (1)
- **Type**: Boolean flag
- **Sets**: `Exchange_Gold_Characters = 1` in device state

### `json_Recive_GiftBox`
Mark gift box collection as complete
- **Type**: Boolean flag
- **Usage**: Sets `Recive_GiftBox = 1` in device state

### `json_Recive_Giftbox_Orbs`
Mark gift box orbs collection as complete
- **Type**: Boolean flag
- **Usage**: Sets `Recive_Giftbox_Orbs = 1` in device state

### `json_Login1_Prepare_Link`
Save account linking preparation status
- **Type**: Boolean flag
- **Usage**: Sets `Login1_Prepare_Link = 1` in device state
- **Purpose**: Indicates account linking preparation is complete

### `json_Account_Linked`
Save account linking status
- **Type**: Boolean flag (True sets to 1)
- **Target**: Device JSON `Account_Linked` key
- **Usage**: Marks account as linked to KLAB ID
- **Purpose**: Tracks linking completion status

### `json_isLinked`
Save account linked status to main isLinked key
- **Type**: Boolean flag (True sets to 1)
- **Target**: Device JSON `isLinked` key
- **Usage**: Marks account as linked, prevents re-linking
- **Purpose**: Main flag that controls login task flow when KLAB account linking is complete

### `json_ScreenShot_MainMenu`
Sets ScreenShot_MainMenu to complete (1)
- **Type**: Boolean flag
- **Sets**: `ScreenShot_MainMenu = 1` in device state

### `json_Kon_Bonaza`
Sets Skip_Kon_Bonaza to complete (1)
- **Type**: Boolean flag
- **Sets**: `Skip_Kon_Bonaza = 1` in device state

### `json_Skip_Yukio_Event`
Sets Skip_Yukio_Event to complete (1)
- **Type**: Boolean flag
- **Sets**: `Skip_Yukio_Event = 1` in device state

### `json_Sort_Characters_Lowest_Level`
Sets Sort_Characters_Lowest_Level to complete (1)
- **Type**: Boolean flag
- **Sets**: `Sort_Characters_Lowest_Level = 1` in device state

### `json_Sort_Filter_Ascension`
Sets Sort_Filter_Ascension to complete (1)
- **Type**: Boolean flag
- **Sets**: `Sort_Filter_Ascension = 1` in device state

### `json_Sort_Multi_Select_Garbage_First`
Sets Sort_Multi_Select_Garbage_First to complete (1)
- **Type**: Boolean flag
- **Sets**: `Sort_Multi_Select_Garbage_First = 1` in device state

### `json_Upgrade_Characters_Level`
Sets Upgrade_Characters_Level to complete (1)
- **Type**: Boolean flag
- **Sets**: `Upgrade_Characters_Level = 1` in device state

### `Increment_Kon_Bonaza`
Increments Skip_Kon_Bonaza_100Times counter by 1
- **Type**: Boolean flag
- **Action**: Increments counter up to 100, sets Skip_Kon_Bonaza to 1 when reaching 100
- **Usage**: Tracks Kon Bonaza skips until completion threshold

### `Increment_Character_Slots_Count`
Increments Character_Slots_Count counter by 1
- **Type**: Boolean flag
- **Action**: Increments counter, sets Character_Slots_Purchase to 1 when reaching 200
- **Usage**: Tracks character slot purchases until completion threshold

### `increment_stock`
Increments global stock counter by 1 in currentlyStock.json
- **Type**: Boolean flag
- **Action**: Increments STOCK value by 1 in device_states/currentlyStock.json
- **Usage**: Tracks global stock/inventory changes across all devices
- **File Location**: `device_states/currentlyStock.json`
- **Auto-Generation**: File automatically created if deleted with default STOCK: 1
- **Timezone**: All timestamps use Istanbul/Europe timezone (+03:00)
- **Format**: `{"STOCK": value, "LastUpdated": "ISO_timestamp_with_timezone"}`
- **Example**: Used in reward collection, mission completion, item gathering tasks
- **Logging**: Shows device name and increment: `[DEVICE1] Stock incremented: 5 → 6`

---

## Task Set Switching Flags

### `BackToStory`
Switch to main story tasks
- **Type**: Boolean flag
- **Target**: `StoryMode_Tasks`

### `BackToRestartingTasks`
Switch to restarting tasks
- **Type**: Boolean flag
- **Target**: `Restarting_Tasks`

### `BackToMain`
Switch to main tasks
- **Type**: Boolean flag
- **Target**: `StoryMode_Tasks`

### `NeedGuildTutorial`
Switch to guild tutorial tasks
- **Type**: Boolean flag
- **Target**: `GUILD_TUTORIAL_TASKS`

### `NeedToRejoin`
Switch to guild rejoin tasks
- **Type**: Boolean flag
- **Target**: `Guild_Rejoin`

### `isRefreshed`
Return to guild tutorial after rejoin
- **Type**: Boolean flag
- **Target**: `GUILD_TUTORIAL_TASKS`

### `Characters_Full`
Switch to sell characters tasks
- **Type**: Boolean flag
- **Target**: `Sell_Characters`

### `SellAccsesurry`
Switch to sell accessory tasks
- **Type**: Boolean flag
- **Target**: `Sell_Accessury`

### `HardStory`
Switch to hard story mode tasks
- **Type**: Boolean flag
- **Target**: `HardStory_Tasks`

### `SideStory`
Switch to side story tasks
- **Type**: Boolean flag
- **Target**: `SideStory`

### `Sub-Stores`
Switch to sub-stories tasks
- **Type**: Boolean flag
- **Target**: `SubStories`

### `CheckSubStoriesAllCleared`
Switch to sub-stories check tasks
- **Type**: Boolean flag
- **Target**: `SubStories_check`

### `Character_Slots_Purchase_Tasks`
Switch to character slots purchase tasks
- **Type**: Boolean flag
- **Target**: `Character_Slots_Purchase`

### `Exchange_Gold_Characters_Tasks`
Switch to exchange gold characters tasks
- **Type**: Boolean flag
- **Target**: `Exchange_Gold_Characters`

### `Recive_GiftBox_Tasks`
Switch to receive gift box tasks
- **Type**: Boolean flag
- **Target**: `Recive_GiftBox`

### `Skip_Kon_Bonaza_Tasks`
Switch to skip Kon Bonanza tasks
- **Type**: Boolean flag
- **Target**: `Skip_Kon_Bonaza`

### `ScreenShot_MainMenu_Tasks`
Switch to screenshot main menu tasks
- **Type**: Boolean flag
- **Target**: `ScreenShot_MainMenu`

### `Skip_Yukio_Event_Tasks`
Switch to skip Yukio Event tasks
- **Type**: Boolean flag
- **Target**: `Skip_Yukio_Event`

### `Sort_Characters_Lowest_Level_Tasks`
Switch to sort characters by lowest level tasks
- **Type**: Boolean flag
- **Target**: `Sort_Characters_Lowest_Level_Tasks`

### `Sort_Filter_Ascension_Tasks`
Switch to sort filter ascension tasks
- **Type**: Boolean flag
- **Target**: `Sort_Filter_Ascension_Tasks`

### `Sort_Multi_Select_Garbage_First_Tasks`
Switch to sort multi-select garbage first tasks
- **Type**: Boolean flag
- **Target**: `Sort_Multi_Select_Garbage_First_Tasks`

### `Upgrade_Characters_Level_Tasks`
Switch to upgrade characters level tasks
- **Type**: Boolean flag
- **Target**: `Upgrade_Characters_Level`

### `Upgrade_Characters_Back_To_Edit_Tasks`
Switch to upgrade characters back to edit tasks
- **Type**: Boolean flag
- **Target**: `Upgrade_Characters_Back_To_Edit`

### `Extract_Orb_Count_Tasks`
Switch to extract orb count tasks
- **Type**: Boolean flag
- **Target**: `Extract_Orb_Counts_Tasks`
- **Usage**: Triggered after main screenshot completion
- **Purpose**: Extracts orb values using enhanced OCR

### `Extract_Account_ID_Tasks`
Switch to extract account ID tasks
- **Type**: Boolean flag
- **Target**: `Extract_Account_ID_Tasks`
- **Usage**: Triggered after orb count extraction completion
- **Purpose**: Extracts player account ID information

### `Login1_Prepare_For_Link_Tasks`
Switch to login preparation tasks
- **Type**: Boolean flag
- **Target**: `login1_prepare_for_link`
- **Usage**: Triggered when ready to start account linking
- **Purpose**: Prepares account for KLAB linking process

### `Login2_Klab_Login_Tasks`
Switch to KLAB login helper tasks
- **Type**: Boolean flag
- **Target**: `login2_klab_login`
- **Usage**: Triggered from login1_prepare_for_link_tasks
- **Purpose**: Handles KLAB account login process

### `Login3_Wait_For_2FA_Tasks`
Switch to 2FA wait helper tasks
- **Type**: Boolean flag
- **Target**: `login3_wait_for_2fa`
- **Usage**: Triggered from login2_klab_login_tasks
- **Purpose**: Waits for 2FA confirmation and handles login completion

### `Login4_Confirm_Link_Tasks`
Switch to confirm link helper tasks
- **Type**: Boolean flag
- **Target**: `login4_confirm_link`
- **Usage**: Triggered from login3_wait_for_2fa_tasks
- **Purpose**: Confirms the final linking process between account and application

### `Endgame_Tasks`
Switch to endgame main tasks
- **Type**: Boolean flag
- **Target**: `endgame`
- **Usage**: Main task set for linked accounts (isLinked = 1)
- **Purpose**: Post-linking progression tasks for fully linked accounts

### `BackToMain_Tasks`
Return to main task set
- **Type**: Boolean flag
- **Target**: `main`
- **Usage**: Used in helper tasks to return to main flow
- **Purpose**: Exits helper task flow and returns to main tasks

### `sync_to_airtable`
Synchronize device data to Airtable
- **Type**: Boolean flag
- **Usage**: Triggers Airtable synchronization process
- **Purpose**: Updates Airtable record with device state data
- **Fields synced**: isLinked, AccountID, UserName, Orbs, Price (calculated)
- **Post-action**: Sets `synced_to_airtable = True` in device state

### `Enter_Email`
Automatically type email from device JSON after clicking
- **Type**: Boolean flag
- **Usage**: After executing click, waits 2 seconds then types email
- **Source**: Uses `Email` field from device JSON state
- **Method**: Uses ADB text input with special character support
- **Example**: `"Enter_Email": true` types email after clicking text field

### `Enter_Password`
Automatically type password from device JSON after clicking
- **Type**: Boolean flag
- **Usage**: After executing click, waits 2 seconds then types password
- **Source**: Uses `Password` field from device JSON state
- **Method**: Uses ADB text input with special character support
- **Security**: Password is masked in logs (shown as asterisks)
- **Example**: `"Enter_Password": true` types password after clicking text field

---

## Conditional Execution Flags

### `StopSupport`
Skip task if specified state flag is true
- **Type**: String (flag name)
- **Example**: `"json_SideMode"` skips if SideMode = 1
- **Usage**: Prevents task from running after certain progress

### `RequireSupport`
Only run task if specified state flag is true
- **Type**: String (flag name)
- **Example**: `"json_Login2_Email_Done"` only runs if email is complete
- **Usage**: Creates sequential task dependencies within same task set
- **Logic**: If requirement is NOT met, task is skipped

### `ConditionalRun`
Only run task if ALL specified conditions are met
- **Type**: Array of state keys
- **Example**: `["EasyMode", "HardMode", "SideMode"]`
- **Usage**: Task only runs if all keys = 1

### `ShowsIn`
Restrict task to specific task sets
- **Type**: Array of task set names
- **Example**: `["storymode_tasks", "restarting_tasks"]`
- **Usage**: Task only active in specified sets

---

## Special Processing Flags

### `HardModeSwipe`
Triggers hard mode swipe sequence
- **Type**: Boolean flag
- **Usage**: Executes special swipe logic for hard mode

### `FullyAnylaze`
Enable comprehensive analysis mode
- **Type**: Boolean flag
- **Usage**: Performs deeper analysis of detected elements

### `extract_orb_value`
Extract orb count value and save to device JSON
- **Type**: Boolean flag
- **Usage**: Automatically extracts and corrects numeric value from OCR and saves to "Orbs" field
- **Requirements**: 
  - Use with `"is_id": false` for number format
  - **Must contain comma**: Only accepts values with comma formatting (e.g., "21,124")
  - Rejects values without commas (e.g., "21124") and continues searching
- **Action**: Converts "211240" → corrects to "21,124" → validates comma → saves to JSON
- **Format**: Saves as string with comma formatting (e.g., "21,124")
- **Validation**: Keeps searching until comma-formatted value is found
- **Example**: Used in orb count extraction tasks

### `extract_orb_value`
Extract orb count and save to device JSON (legacy single-attempt)
- **Type**: Boolean flag
- **Usage**: Automatically extracts orb count from OCR and saves to "Orbs" field
- **Requirements**: Use with OCR tasks that target orb display area
- **Pattern**: Expects comma-formatted numbers (e.g., "21,234")
- **Action**: Applies pattern correction and saves to JSON "Orbs" field
- **Example**: Used in legacy orb extraction tasks

### `temp_orb_storage`
Temporarily store orb extraction attempt for consensus
- **Type**: Boolean flag
- **Usage**: Stores OCR result temporarily for multi-attempt consensus checking
- **Requirements**: Use with `orb_extraction_attempt` number
- **Action**: Stores cleaned OCR result in memory for comparison
- **Purpose**: Part of 4-attempt consensus system for accurate orb extraction

### `orb_consensus_check`
Perform consensus check on orb extraction attempts
- **Type**: Boolean flag
- **Usage**: Triggers consensus analysis of all 4 orb extraction attempts
- **Logic**: Finds values that appear 2+ times among attempts
- **Action**: Saves consensus value to "Orbs" field, or fails if no consensus
- **Purpose**: Final step in 4-attempt consensus system for 0% error rate

### `orb_extraction_attempt`
Mark which attempt number this orb extraction is
- **Type**: Integer (1-4)
- **Usage**: Identifies which of the 4 attempts this OCR extraction represents
- **Required with**: `temp_orb_storage` or `orb_consensus_check` flags
- **Purpose**: Tracks attempt sequence for consensus system

### `extract_account_id_value`
Extract account ID value and save to device JSON (legacy single-attempt)
- **Type**: Boolean flag
- **Usage**: Automatically extracts ID text from OCR and saves to "AccountID" field
- **Requirements**: Use with `"is_id": true` for ID format
- **Action**: Extracts "ID: 88 534 886" → saves "ID: 88 534 886" to JSON "AccountID" field
- **Example**: Used in legacy account ID extraction tasks

### `temp_account_id_storage`
Temporarily store account ID extraction attempt for consensus
- **Type**: Boolean flag
- **Usage**: Stores OCR result temporarily for multi-attempt consensus checking
- **Requirements**: Use with `account_id_extraction_attempt` number
- **Action**: Stores cleaned OCR result in memory for comparison
- **Purpose**: Part of 4-attempt consensus system for accurate Account ID extraction

### `account_id_consensus_check`
Perform consensus check on account ID extraction attempts
- **Type**: Boolean flag
- **Usage**: Triggers consensus analysis of all 4 account ID extraction attempts
- **Logic**: Finds values that appear 2+ times among attempts
- **Action**: Saves consensus value to "AccountID" field, or fails if no consensus
- **Purpose**: Final step in 4-attempt consensus system for 100% accuracy

### `account_id_extraction_attempt`
Mark which attempt number this account ID extraction is
- **Type**: Integer (1-4)
- **Usage**: Identifies which of the 4 attempts this OCR extraction represents
- **Required with**: `temp_account_id_storage` or `account_id_consensus_check` flags
- **Purpose**: Tracks attempt sequence for consensus system

### `save_screenshot_with_username`
Take screenshot and save with current stock, device number and username from device state
- **Type**: Boolean flag
- **Usage**: Captures current screen and saves to stock_images folder
- **Filename**: Uses current stock + device number + `UserName` field (e.g., "15_8_Player.png")
- **Format**: `{CurrentStock}_{DeviceNumber}_{UserName}.png`
- **Directory**: `stock_images/`
- **Image Format**: PNG image, cropped to roi [160, 0, 779, 540]
- **Purpose**: Account documentation and verification with stock tracking and device identification
- **Trigger**: Only when pixel detection task is matched
- **Example**: Used in main menu screenshot tasks
- **Stock Integration**: Automatically includes current global stock value in filename

### `type_text`
Types text from device JSON into input fields
- **Type**: String with template placeholders
- **Usage**: Types specified text after clicking
- **Placeholders**: 
  - `{{Email}}` - Uses device's Email field
  - `{{Password}}` - Uses device's Password field
  - `{{UserName}}` - Uses device's UserName field
- **Example**: `"type_text": "{{Email}}"` types the email address
- **Requirement**: Must be used with pixel tasks that click input fields

---

## Task Naming Convention

### `task_name` (Required)
Descriptive name for the task
- **Format**: Clear, action-oriented description
- **Example**: `"Click [Skip]"`, `"Open Story Window"`
- **Special Markers**:
  - `[Text]` - Indicates UI button/element
  - `#1, #2` - Different variations of same task
  - `[Multi: X]` - Multiple clicks performed
  - `[OCR: 'text']` - OCR detection result

---

## Example Task Definitions

### Basic Pixel Task
```python
{
    "task_name": "Click [Next Quest]",
    "type": "pixel",
    "click_location_str": "756,508",
    "search_array": ["713,512","#ffffff","760,507","#ffffff"],
    "isLogical": False,
    "priority": 5,
    "cooldown": 5.0,
    "shared_detection": True,
    "use_match_position": False,
    "StopSupport": "json_SideMode",
    "ConditionalRun": ["EasyMode", "HardMode"],
    "BackToMain": True,
    "sleep": 2.0
}
```

### Enhanced OCR Task (Regular Numbers)
```python
{
    "task_name": "Extract Orb Count",
    "type": "ocr",
    "roi": [711, 6, 75, 27],
    "is_id": false,
    "extract_orb_value": true,
    "cooldown": 5.0,
    "Extract_Account_ID_Tasks": true
}
```

### Enhanced OCR Task (ID Format)
```python
{
    "task_name": "Extract Player ID",
    "type": "ocr",
    "roi": [100, 300, 300, 50],
    "is_id": true,
    "cooldown": 2.0,
    "use_match_position": false
}
```

### Screenshot Task with Stock and Username
```python
{
    "task_name": "Take Main Menu Screenshot",
    "type": "pixel",
    "click_location_str": "0,0",
    "search_array": ["960,540", "#000000"],
    "save_screenshot_with_username": true,  # Saves as: {Stock}_{Device}_{User}.png
    "json_ScreenShot_MainMenu": true,
    "Extract_Orb_Count_Tasks": true,
    "cooldown": 1.0
}
```

### Stock Management Task
```python
{
    "task_name": "Collect Daily Reward [Stock Tracking]",
    "type": "pixel",
    "click_location_str": "480,350",
    "search_array": ["450,320","#FFD700","510,380","#FFD700"],
    "increment_stock": true,  # Increment global stock counter
    "cooldown": 3.0,
    "priority": 15,
    "sleep": 1.5
}
```

### Login Flow Tasks
```python
# Main Task - Login Preparation
{
    "task_name": "Detect Link Account Button [Prepare for Link]",
    "type": "pixel",
    "click_location_str": "960,640",
    "search_array": ["900,600","#4CAF50","1020,600","#4CAF50"],
    "Login2_Klab_Login_Tasks": true,  # Trigger helper
    "json_Login1_Prepare_Link": true,
    "NextTaskSet_Tasks": true
}

# Helper Task - KLAB Login
{
    "task_name": "Click [Email TextBox] [KLAB Login]",
    "type": "template",
    "template_path": "templates/Login/Email.png",
    "confidence": 0.90,
    "use_match_position": true,
    "Enter_Email": true,  # Auto-type email after click
    "cooldown": 99.0,
    "sleep": 3
}

# Helper Task - 2FA Wait
{
    "task_name": "Detect Login Success [Wait for 2FA]",
    "type": "pixel",
    "click_location_str": "0,0",
    "search_array": ["400,200","#00C853"],
    "BackToMain_Tasks": true,  # Return to main
    "json_Account_Linked": true
}
```

---

## Notes

- Tasks are processed in priority order (lowest number first)
- Multiple flags can be combined in a single task
- State changes persist across game sessions
- Task switching happens immediately when flag is triggered
- Cooldowns prevent task spam and improve stability
- Conditional flags allow dynamic task flow based on progress
- **Timezone Handling**: All timestamps in device states and stock files use Istanbul/Europe timezone (+03:00), regardless of system location
- **Stock Management**: The `increment_stock` flag works globally across all devices and auto-generates the stock file if deleted
- **Auto-Generation**: Stock and device state files are automatically created/restored with default values if corrupted or deleted