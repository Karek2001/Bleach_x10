# airtable_stock_fetcher.py - Fetches account details from Airtable based on stock and device order
import requests
import json
import os
import asyncio
from typing import Optional, Dict
from device_state_manager import device_state_manager

# Airtable configuration (same as airtable_sync.py)
AIRTABLE_API_KEY = "pat2QVZVjoGSSut65.eb423fef85c745815abb18269e6253021c058f4353c88ec59013efb6395de3d4"
AIRTABLE_BASE_ID = "appHpjTJPFvsRvorc"
AIRTABLE_TABLE_ID = "tblly72Bpidn8qE2v"
AIRTABLE_BASE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"

async def get_stock_account_details(device_id: str, order_number: int, stock_number: int) -> Optional[Dict]:
    """
    Fetch account details from Airtable based on Order and Stock number
    
    Args:
        device_id: Device identifier (e.g., DEVICE1)
        order_number: Order number (1-10 based on device number)
        stock_number: Current stock number from currentlyStock.json
    
    Returns:
        Dictionary with Email, Password, UserName or None if not found
    """
    try:
        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Create formula to search for matching record
        # Airtable formula: AND({Order} = order_number, {STOCK} = stock_number)
        formula = f"AND({{Order}} = {order_number}, {{STOCK}} = {stock_number})"
        
        params = {
            "filterByFormula": formula,
            "maxRecords": 1  # We only need one matching record
        }
        
        print(f"[{device_id}] 🔍 Searching Airtable for Order={order_number}, STOCK={stock_number}")
        
        response = requests.get(AIRTABLE_BASE_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            if records:
                record = records[0]['fields']
                account_details = {
                    'Email': record.get('Email', ''),
                    'Password': record.get('Password', ''),
                    'UserName': record.get('UserName', '')
                }
                
                print(f"[{device_id}] ✅ Found account details:")
                print(f"    Email: {account_details['Email']}")
                print(f"    UserName: {account_details['UserName']}")
                print(f"    Password: {'*' * len(account_details['Password']) if account_details['Password'] else 'N/A'}")
                
                return account_details
            else:
                print(f"[{device_id}] ⚠️ No matching record found for Order={order_number}, STOCK={stock_number}")
                return None
        else:
            print(f"[{device_id}] ❌ Airtable API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"[{device_id}] ❌ Error fetching stock account details: {e}")
        return None

async def check_and_fetch_all_accounts():
    """
    Check if all devices have isLinked=1 and fetch account details if true
    Also handles clearing device JSON files and regenerating them
    """
    try:
        # Check if all 10 devices have isLinked = 1
        all_linked = True
        device_states = {}
        
        for i in range(1, 11):
            device_id = f"DEVICE{i}"
            state = device_state_manager.get_state(device_id)
            device_states[device_id] = state
            
            if not state.get("isLinked", False):
                all_linked = False
                print(f"[{device_id}] Not linked yet (isLinked={state.get('isLinked', False)})")
        
        if not all_linked:
            print("[System] Not all devices are linked yet. Skipping account fetch.")
            return False
        
        print("[System] ✅ All devices are linked! Starting account fetch process...")
        
        # Get current stock number
        stock_file_path = os.path.join(device_state_manager.state_dir, "currentlyStock.json")
        if os.path.exists(stock_file_path):
            with open(stock_file_path, 'r') as f:
                stock_data = json.load(f)
                stock_number = stock_data.get('STOCK', 999)
        else:
            print("[System] ⚠️ currentlyStock.json not found, using default stock 999")
            stock_number = 999
        
        print(f"[System] Current STOCK number: {stock_number}")
        
        # Delete all device JSON files first AND clear cache
        print("[System] 🗑️ Deleting all device JSON files and clearing cache...")
        for i in range(1, 11):
            device_id = f"DEVICE{i}"
            device_file = os.path.join(device_state_manager.state_dir, f"{device_id}.json")
            if os.path.exists(device_file):
                os.remove(device_file)
                print(f"[System] Deleted {device_id}.json")
            
            # CRITICAL: Clear from memory cache for both DEVICE name and IP address
            # Clear DEVICE name from cache
            if device_id in device_state_manager.states:
                del device_state_manager.states[device_id]
            # Clear IP address from cache
            ip_address = device_state_manager.reverse_mapping.get(device_id)
            if ip_address and ip_address in device_state_manager.states:
                del device_state_manager.states[ip_address]
        
        # Now fetch and create new device files with account details
        print("[System] 📥 Fetching account details from Airtable and creating new device files...")
        
        for i in range(1, 11):
            device_id = f"DEVICE{i}"
            order_number = i  # Device number corresponds to Order field
            
            # Fetch account details from Airtable
            account_details = await get_stock_account_details(device_id, order_number, stock_number)
            
            if account_details:
                # Create new device state with account details and reroll fields
                # Using the exact field order requested by user
                new_state = {
                    "AccountID": "",
                    "UserName": account_details.get('UserName', 'Player'),
                    "Email": account_details.get('Email', ''),
                    "Password": account_details.get('Password', ''),
                    "isLinked": 0,  # Reset to 0 for new cycle
                    "Orbs": "0",
                    "RestartingCount": 0,
                    "Reroll_Earse_GameData": 0,
                    "Reroll_Tutorial_FirstMatch": 0,
                    "Reroll_Tutorial_CharacterChoose": 0,
                    "Reroll_Tutorial_SecondMatch": 0,
                    "Reroll_ReplaceIchigoWithFiveStar": 0,
                    "EasyMode": 0,
                    "HardMode": 0,
                    "SideMode": 0,
                    "SubStory": 0,
                    "Character_Slots_Purchased": 0,
                    "Exchange_Gold_Characters": 0,
                    "Recive_GiftBox": 0,
                    "Skip_Kon_Bonaza_100Times": 0,
                    "Skip_Kon_Bonaza": 0,
                    "Character_Slots_Count": 0,
                    "ScreenShot_MainMenu": 0,
                    "Skip_Yukio_Event": 0,
                    "Skip_Yukio_Event_Retry_Count": 0,
                    "Sort_Characters_Lowest_Level": 0,
                    "Sort_Filter_Ascension": 0,
                    "Sort_Multi_Select_Garbage_First": 0,
                    "Upgrade_Characters_Level": 0,
                    "Recive_Giftbox_Orbs": 0,
                    "Login1_Prepare_Link": 0,
                    "Account_Linked": 0,
                    "Login2_Email_Done": 0,
                    "Login2_Password_Done": 0,
                    "Login2_Cloudflare_Done": 0,
                    "synced_to_airtable": False,
                    "LastUpdated": datetime.now().isoformat(),
                    "CurrentTaskSet": "reroll_earse_gamedata",
                    "SessionStats": {
                        "SessionStartTime": datetime.now().isoformat(),
                        "TasksExecuted": 0,
                        "LastTaskExecuted": None
                    }
                }
                
                # Save the new state directly using device_state_manager
                # IMPORTANT: Convert DEVICE name to IP address for consistency
                ip_address = device_state_manager.reverse_mapping.get(device_id)
                if ip_address:
                    device_state_manager.states[ip_address] = new_state
                    device_state_manager._save_state(ip_address)
                else:
                    # Fallback if no mapping found
                    device_state_manager.states[device_id] = new_state
                    device_state_manager._save_state(device_id)
                print(f"[{device_id}] ✅ Created new device file with account details:")
                print(f"    Email: {account_details.get('Email', '')}")
                print(f"    UserName: {account_details.get('UserName', '')}")
            else:
                print(f"[{device_id}] ⚠️ No account details found, creating minimal device file")
                # Create minimal device file without account details
                minimal_state = device_state_manager._get_default_state()
                # IMPORTANT: Convert DEVICE name to IP address for consistency
                ip_address = device_state_manager.reverse_mapping.get(device_id)
                if ip_address:
                    device_state_manager.states[ip_address] = minimal_state
                    device_state_manager._save_state(ip_address)
                else:
                    # Fallback if no mapping found
                    device_state_manager.states[device_id] = minimal_state
                    device_state_manager._save_state(device_id)
        
        # Increment stock number for next batch
        stock_number += 1
        stock_data = {
            "STOCK": stock_number,
            "LastUpdated": datetime.now().isoformat()
        }
        with open(stock_file_path, 'w') as f:
            json.dump(stock_data, f, indent=2)
        print(f"[System] ✅ Incremented STOCK to {stock_number} for next batch")
        
        return True
        
    except Exception as e:
        print(f"[System] ❌ Error in check_and_fetch_all_accounts: {e}")
        return False

# Import datetime for timestamps
from datetime import datetime
