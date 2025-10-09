#!/usr/bin/env python3
# quick_airtable_import.py - Quick utility for Airtable import by Order & STOCK
from airtable_import import import_all_devices_by_stock, import_device_by_order, get_current_stock_number
from device_state_manager import device_state_manager
import sys

def quick_import_all():
    """Quickly import all devices using Order and STOCK"""
    print("🚀 QUICK IMPORT: Importing all devices by Order & STOCK...")
    stats = import_all_devices_by_stock()
    
    print(f"\n✅ Complete! Imported {stats['imported']} devices from STOCK {stats['stock_number']}, {stats['errors']} errors")
    return stats

def quick_import_device(device_name):
    """Quickly import a specific device by its Order number"""
    print(f"🚀 QUICK IMPORT: Importing {device_name} by Order & STOCK...")
    
    # Extract device number from name (e.g., DEVICE1 -> 1)
    try:
        device_num = int(device_name.replace("DEVICE", ""))
        if device_num < 1 or device_num > 10:
            print(f"❌ Invalid device number. Use DEVICE1-DEVICE10")
            return False
    except ValueError:
        print(f"❌ Invalid device name format. Use DEVICE1, DEVICE2, etc.")
        return False
    
    # Get current stock number
    stock_number = get_current_stock_number()
    
    # Import using Order (device number) and STOCK
    success = import_device_by_order(device_name, device_num, stock_number)
    
    if success:
        print(f"\n✅ Successfully imported {device_name} from Order={device_num}, STOCK={stock_number}")
    else:
        print(f"\n❌ Failed to import {device_name}")
    
    return success

def show_stock_status():
    """Show current STOCK number and device import status"""
    print("👀 PREVIEW: Showing STOCK status and device info...")
    
    # Get current stock number
    stock_number = get_current_stock_number()
    
    imported_count = 0
    not_imported_count = 0
    
    print(f"\n📦 Current STOCK: {stock_number}")
    print("-" * 70)
    print(f"{'Device':<8} | {'Order':<5} | {'Email':<25} | {'Status':<12}")
    print("-" * 70)
    
    for i in range(1, 11):
        device_id = f"DEVICE{i}"
        device_data = device_state_manager.get_state(device_id)
        email = device_data.get("Email", "")
        imported = device_data.get("imported_from_airtable", False)
        
        if imported:
            status = "✅ IMPORTED"
            imported_count += 1
        else:
            status = "🟢 READY"
            not_imported_count += 1
        
        email_display = email[:25] if email else "No email"
        print(f"{device_id:<8} | {i:<5} | {email_display:<25} | {status}")
    
    print("-" * 70)
    print(f"📊 STOCK {stock_number}: {imported_count} imported, {not_imported_count} ready")
    
    return {
        "stock_number": stock_number,
        "imported": imported_count,
        "ready": not_imported_count
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python quick_airtable_import.py preview       # Show STOCK status")
        print("  python quick_airtable_import.py import        # Import all devices by Order & STOCK")
        print("  python quick_airtable_import.py device DEVICE1 # Import specific device")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "preview":
            show_stock_status()
        elif command == "import":
            quick_import_all()
        elif command == "device":
            if len(sys.argv) < 3:
                print("❌ Please specify device name (e.g., DEVICE1)")
                sys.exit(1)
            device_name = sys.argv[2].upper()
            quick_import_device(device_name)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
