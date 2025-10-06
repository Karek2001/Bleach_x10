# Airtable Sync Updates - S3 and Screenshot Format

## 📋 Overview
Updated airtable_sync.py to handle the new screenshot naming format and S3 bucket configuration as requested.

## ✅ Changes Made

### 🪣 **S3 Bucket Configuration:**
- **OLD:** `db-legends-aggstore`
- **NEW:** `bbs-aggstore`
- **Location:** Line 19 in `airtable_sync.py`

### 📁 **S3 Upload Structure:**
- **OLD:** Images uploaded to folders by device (`bleach_devices/{device_id}/{filename}`)
- **NEW:** Images uploaded directly to bucket root (`{filename}`)
- **Change:** Removed folder structure completely
- **Location:** Lines 90-92 in `upload_image_to_s3()` function

### 🖼️ **Screenshot Filename Format:**
- **OLD FORMAT:** `DeviceNumber_UserName.png` (e.g., `1_Player.png`)
- **NEW FORMAT:** `Stock_DeviceNumber_UserName.png` (e.g., `15_1_Player.png`)
- **Dynamic Stock:** Stock value retrieved from `currentlyStock.json` at runtime
- **Location:** `get_image_path_for_device()` function completely rewritten

## 🔧 Implementation Details

### **New Image Path Detection Logic:**
1. **Primary:** Look for new format: `{Stock}_{DeviceNumber}_{UserName}.png`
2. **AccountID Fallback:** If username is "Player", try `{Stock}_{DeviceNumber}_ID{numbers}.png`
3. **Backward Compatibility:** Fall back to old format if new format doesn't exist
4. **Smart Priority:** New format always preferred over old format

### **S3 Upload Changes:**
```python
# OLD S3 Key Format:
s3_key = f"bleach_devices/{device_id}/{filename}"
# Result: s3://db-legends-aggstore/bleach_devices/127.0.0.1:16800/1_Player.png

# NEW S3 Key Format:
s3_key = filename
# Result: s3://bbs-aggstore/15_1_Player.png
```

### **Filename Detection Examples:**
```python
# Stock = 25, Device = DEVICE1, User = Player
Old format: "1_Player.png"
New format: "25_1_Player.png"

# Stock = 50, Device = DEVICE10, User = TestUser  
Old format: "10_TestUser.png"
New format: "50_10_TestUser.png"

# Stock = 100, Device = DEVICE3, User = Player, AccountID = "ID: 88 534 886"
Old format: "3_Player.png" or "3_ID885348.png"
New format: "100_3_Player.png" or "100_3_ID885348.png"
```

## 🧪 Testing Results

### **Verified Functionality:**
- ✅ **Bucket Name:** Changed to `bbs-aggstore`
- ✅ **No Folders:** Files uploaded directly to bucket root
- ✅ **New Format Detection:** Correctly finds `{Stock}_{Device}_{User}.png`
- ✅ **Backward Compatibility:** Falls back to old format when needed
- ✅ **AccountID Fallback:** Works with new stock format
- ✅ **Dynamic Stock:** Stock value updated in real-time from currentlyStock.json
- ✅ **Priority Logic:** New format preferred over old format

### **Example S3 URLs:**
```
OLD: https://fsn1.your-objectstorage.com/db-legends-aggstore/bleach_devices/127.0.0.1:16800/1_Player.png
NEW: https://fsn1.your-objectstorage.com/bbs-aggstore/15_1_Player.png
```

## 📊 Benefits

### **Improved Organization:**
- **Stock Tracking:** Screenshot names now include current stock value
- **Simplified S3:** No nested folder structure to manage
- **Dynamic Naming:** Filenames automatically update with stock changes
- **Better Identification:** Easy to see stock level from filename

### **Backward Compatibility:**
- **Seamless Migration:** Existing old format files still work
- **No Data Loss:** System gracefully handles both formats
- **Smart Fallback:** Automatically detects best available format

## 🔄 Migration Behavior

### **Automatic Handling:**
1. **New Screenshots:** Saved with new format `{Stock}_{Device}_{User}.png`
2. **Airtable Sync:** Looks for new format first, falls back to old if needed
3. **S3 Upload:** Always uploads to bucket root regardless of format
4. **No Manual Migration:** System handles transition automatically

## 🚀 Ready for Production
The airtable sync system now:
- Uses the correct S3 bucket (`bbs-aggstore`)
- Uploads files directly to bucket root (no folders)
- Handles the new stock-based screenshot naming
- Maintains backward compatibility with existing screenshots
- Dynamically includes current stock value in all operations
