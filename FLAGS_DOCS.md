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
Sets Recive_GiftBox to complete (1)
- **Type**: Boolean flag
- **Sets**: `Recive_GiftBox = 1` in device state

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

---

## Conditional Execution Flags

### `StopSupport`
Skip task if specified state flag is true
- **Type**: String (flag name)
- **Example**: `"json_SideMode"` skips if SideMode = 1
- **Usage**: Prevents task from running after certain progress

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

## Example Task Definition

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

---

## Notes

- Tasks are processed in priority order (lowest number first)
- Multiple flags can be combined in a single task
- State changes persist across game sessions
- Task switching happens immediately when flag is triggered
- Cooldowns prevent task spam and improve stability
- Conditional flags allow dynamic task flow based on progress