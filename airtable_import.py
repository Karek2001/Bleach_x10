#!/usr/bin/env python3
# airtable_import.py - Import data FROM Airtable TO device JSON files (works like airtable_stock_fetcher.py)
import requests
import json
import os
from datetime import datetime
from device_state_manager import device_state_manager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Airtable configuration (same as airtable_stock_fetcher.py)
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
AIRTABLE_BASE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"

def get_current_stock_number():
    """Get current stock number from currentlyStock.json (same as airtable_stock_fetcher.py)"""
    stock_file_path = os.path.join(device_state_manager.state_dir, "currentlyStock.json")
    if os.path.exists(stock_file_path):
        with open(stock_file_path, 'r') as f:
            stock_data = json.load(f)
            return stock_data.get('STOCK', 999)
    else:
        print("[System] ⚠️ currentlyStock.json not found, using default stock 999")
        return 999

def get_stock_account_details(device_id: str, order_number: int, stock_number: int):
    """Fetch account details from Airtable by Order and STOCK (same as airtable_stock_fetcher.py)"""
    try:
        headers = {
            "Authorization": f"Bearer {AIRTABLE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Create formula to search for matching record (same as stock_fetcher)
        formula = f"AND({{Order}} = {order_number}, {{STOCK}} = {stock_number})"
        
        params = {
            "filterByFormula": formula,
            "maxRecords": 1
        }
        
        print(f"[{device_id}] 🔍 Searching Airtable for Order={order_number}, STOCK={stock_number}")
        
        response = requests.get(AIRTABLE_BASE_URL, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            if records:
                return records[0]  # Return full record
            else:
                print(f"[{device_id}] ⚠️ No matching record found for Order={order_number}, STOCK={stock_number}")
                return None
        else:
            print(f"[{device_id}] ❌ Airtable API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"[{device_id}] ❌ Error fetching account details: {e}")
        return None

def import_device_by_order(device_id: str, order_number: int, stock_number: int):
    """Import device data by Order and STOCK number (same logic as airtable_stock_fetcher.py)"""
    print(f"[{device_id}] Starting import for Order={order_number}, STOCK={stock_number}")
    
    # Get record from Airtable
    record = get_stock_account_details(device_id, order_number, stock_number)
    
    if not record:
        print(f"[{device_id}] ❌ No record found in Airtable")
        return False
    
    # Extract account details
    fields = record.get('fields', {})
    account_details = {
        'Email': fields.get('Email', ''),
        'Password': fields.get('Password', ''),
        'UserName': fields.get('UserName', ''),
        'AccountID': fields.get('AccountID', ''),
        'Orbs': fields.get('Orbs', '0'),
        'isLinked': fields.get('isLinked', False)
    }
    
    print(f"[{device_id}] ✅ Found account details:")
    print(f"    Email: {account_details['Email']}")
    print(f"    UserName: {account_details['UserName']}")
    print(f"    AccountID: {account_details['AccountID']}")
    print(f"    Orbs: {account_details['Orbs']}")
    
    # Update device with imported data
    success = update_device_from_record(device_id, account_details)
    
    if success:
        # Mark as imported
        device_state_manager.update_state(device_id, "imported_from_airtable", True)
        device_state_manager.update_state(device_id, "LastImportedFromAirtable", datetime.now().isoformat())
        print(f"[{device_id}] ✅ Import complete")
        return True
    else:
        print(f"[{device_id}] ❌ Import failed")
        return False

def update_device_from_record(device_id: str, account_details: dict):
    """Update device with account details from Airtable"""
    try:
        updates = {}
        
        # Email
        if account_details.get('Email'):
            updates["Email"] = account_details['Email']
        
        # Password
        if account_details.get('Password'):
            updates["Password"] = account_details['Password']
        
        # UserName
        if account_details.get('UserName'):
            updates["UserName"] = account_details['UserName']
        
        # AccountID
        if account_details.get('AccountID'):
            updates["AccountID"] = str(account_details['AccountID'])
        
        # Orbs (clean up formatting)
        if account_details.get('Orbs'):
            orbs_value = str(account_details['Orbs']).replace(",", "")
            updates["Orbs"] = orbs_value
        
        # isLinked (handle different formats)
        if 'isLinked' in account_details:
            is_linked = account_details['isLinked']
            if isinstance(is_linked, str):
                is_linked = is_linked.lower() == "true"
            elif isinstance(is_linked, int):
                is_linked = bool(is_linked)
            
            updates["isLinked"] = is_linked
            updates["Account_Linked"] = 1 if is_linked else 0
        
        # Apply updates
        updated_count = 0
        for field, value in updates.items():
            old_value = device_state_manager.get_state(device_id).get(field)
            if old_value != value:
                device_state_manager.update_state(device_id, field, value)
                print(f"[{device_id}] ✓ Updated {field}: {old_value} → {value}")
                updated_count += 1
        
        print(f"[{device_id}] Updated {updated_count} fields")
        return True
        
    except Exception as e:
        print(f"[{device_id}] Error updating device: {e}")
        return False
def import_all_devices_by_stock():
    """Import all devices using Order and STOCK (same logic as airtable_stock_fetcher.py)"""
    print("🔄 Starting import from Airtable using Order and STOCK...")
    
    # Get current stock number
    stock_number = get_current_stock_number()
    print(f"[System] Current STOCK number: {stock_number}")
    
    imported_count = 0
    error_count = 0
    not_found_count = 0
    
    # Process devices 1-10 (same as stock_fetcher)
    for i in range(1, 11):
        device_id = f"DEVICE{i}"
        order_number = i  # Device number = Order number
        
        try:
            success = import_device_by_order(device_id, order_number, stock_number)
            if success:
                imported_count += 1
            else:
                not_found_count += 1
        except Exception as e:
            print(f"[{device_id}] Error during import: {e}")
            error_count += 1
    
    # Print summary
    print("\n" + "="*60)
    print("📊 STOCK IMPORT SUMMARY")
    print("="*60)
    print(f"📦 STOCK Number: {stock_number}")
    print(f"✅ Successfully imported: {imported_count}")
    print(f"❌ Errors: {error_count}")
    print(f"🔍 Not found in Airtable: {not_found_count}")
    print("="*60)
    
    return {
        "stock_number": stock_number,
        "imported": imported_count,
        "errors": error_count,
        "not_found": not_found_count
    }

def main():
    """Main function - works like airtable_stock_fetcher.py but for importing"""
    print("📥 AIRTABLE IMPORT BY ORDER & STOCK")
    print("This imports data FROM Airtable using Order and STOCK numbers")
    print()
    
    try:
        # Import all devices using Order and STOCK
        stats = import_all_devices_by_stock()
        
        if stats["imported"] > 0:
            print(f"\n🎉 Success! Imported {stats['imported']} devices from STOCK {stats['stock_number']}")
        else:
            print(f"\n⚠️ No devices imported from STOCK {stats['stock_number']}. Check if records exist in Airtable.")
            
    except KeyboardInterrupt:
        print("\n🛑 Import cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
