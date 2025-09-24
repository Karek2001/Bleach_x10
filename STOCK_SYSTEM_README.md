# Stock Management System with Istanbul Timezone

## 📋 Overview
This document describes the newly implemented stock management system that tracks global inventory changes across all devices with Istanbul/Europe timezone support.

## ✅ Features Implemented

### 🎯 Core Functionality
- **Global Stock Counter**: Tracks stock value across all devices in `device_states/currentlyStock.json`
- **Auto-Generation**: File automatically recreated if deleted or corrupted
- **Istanbul Timezone**: All timestamps use Europe/Istanbul timezone (+03:00), even when running from Germany
- **Task Integration**: Simple `"increment_stock": true` flag in tasks

### 📁 File Structure
```json
{
  "STOCK": 5,
  "LastUpdated": "2025-09-24T12:46:10.993082+03:00"
}
```

## 🔧 Implementation Details

### Device State Manager Updates
- Added `_get_istanbul_time()` method for timezone conversion
- Added `increment_stock()`, `get_current_stock()`, `set_stock()` methods
- Updated all datetime operations to use Istanbul timezone
- Auto-generation and integrity checking for stock file

### Background Process Integration
- Added increment_stock flag processing in task execution flow
- Integrates with existing JSON flag system in `background_process.py`

### Documentation Updates
- Updated `FLAGS_DOCS.md` with complete increment_stock documentation
- Added example tasks and timezone handling notes
- `requirements.txt` already contained pytz==2023.3

## 🎮 Usage Examples

### Basic Task with Stock Increment
```python
{
    "task_name": "Collect Daily Reward [Stock Tracking]",
    "type": "pixel",
    "click_location_str": "480,350",
    "search_array": ["450,320","#FFD700","510,380","#FFD700"],
    "increment_stock": true,  # Increment global stock counter
    "cooldown": 3.0,
    "priority": 15
}
```

### OCR Task with Stock Tracking
```python
{
    "task_name": "OCR Item Collection Detection",
    "type": "ocr",
    "ocr_text": "item collected,reward received",
    "roi": [100, 150, 200, 50],
    "increment_stock": true,  # Track collection
    "cooldown": 2.0
}
```

### Template Task with Stock Counter
```python
{
    "task_name": "Complete Mission Button",
    "type": "template",
    "template_path": "templates/complete_mission.png",
    "threshold": 0.8,
    "increment_stock": true,  # Track completion
    "cooldown": 5.0
}
```

## 🧪 Testing
The system has been thoroughly tested with:
- ✅ Auto-generation when file is deleted
- ✅ Stock increment functionality
- ✅ Istanbul timezone conversion (Germany → Istanbul +03:00)
- ✅ File integrity and error handling
- ✅ Integration with existing task system

## 📝 API Methods

### DeviceStateManager Methods
```python
# Get current stock value
stock = device_state_manager.get_current_stock()

# Increment stock (with optional device logging)
new_stock = device_state_manager.increment_stock("127.0.0.1:16800")

# Set stock to specific value
device_state_manager.set_stock(10, "127.0.0.1:16832")
```

## 🌍 Timezone Behavior
- **System Time**: Shows local time (e.g., Germany)
- **File Timestamps**: Always Istanbul/Europe timezone (+03:00)
- **Conversion**: Automatic UTC → Istanbul conversion
- **Fallback**: Uses system timezone if pytz unavailable

## 📊 Logging Examples
```
[STOCK] File missing, auto-generating currentlyStock.json
[DEVICE1] Stock incremented: 1 → 2
[DEVICE2] Stock incremented: 2 → 3
[DEVICE3] Stock set: 5 → 10
```

## 🔗 Files Modified
1. `device_state_manager.py` - Core stock management functionality
2. `background_process.py` - Task flag processing integration
3. `FLAGS_DOCS.md` - Complete documentation update
4. `device_states/currentlyStock.json` - Auto-generated stock file

## 🚀 Ready for Production
The stock management system is now fully integrated and ready for use. Simply add `"increment_stock": true` to any task to track inventory changes with Istanbul timezone timestamps.
