#!/usr/bin/env python3
"""
Test script for Airtable sync functionality with S3 integration
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from airtable_sync import (
    sync_device_to_airtable, 
    get_image_path_for_device, 
    upload_image_to_airtable,
    upload_image_to_s3,
    initialize_s3,
    find_record_by_email,
    calculate_price_from_orbs,
    get_device_id_from_name,
    s3_client,
    S3_BUCKET_NAME,
    S3_ENDPOINT
)
from device_state_manager import device_state_manager

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f" {text}")
    print(f"{'='*60}")

def print_step(step_num, text):
    """Print a formatted step"""
    print(f"\n🔸 Step {step_num}: {text}")

def test_s3_connection():
    """Test S3 connection and configuration"""
    print_header("TESTING S3 CONNECTION")
    
    print_step(1, "Checking S3 configuration")
    print(f"   S3 Endpoint: {S3_ENDPOINT}")
    print(f"   S3 Bucket: {S3_BUCKET_NAME}")
    
    print_step(2, "Testing S3 client initialization")
    if s3_client is None:
        print("   ❌ S3 client not initialized")
        print("   Trying to initialize...")
        if initialize_s3():
            print("   ✅ S3 client initialized successfully")
        else:
            print("   ❌ Failed to initialize S3 client")
            return False
    else:
        print("   ✅ S3 client already initialized")
    
    print_step(3, "Testing S3 bucket access")
    try:
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        print("   ✅ S3 bucket accessible")
        return True
    except Exception as e:
        print(f"   ❌ S3 bucket access failed: {e}")
        return False

def test_device_data(device_name="DEVICE10"):
    """Test device data loading and parsing"""
    print_header(f"TESTING DEVICE DATA ({device_name})")
    
    print_step(1, "Converting device name to device_id")
    device_id = get_device_id_from_name(device_name)
    if not device_id:
        print(f"   ❌ Could not find device_id for {device_name}")
        return None, None
    print(f"   Device name: {device_name} → Device ID: {device_id}")
    
    print_step(2, "Loading device state")
    device_data = device_state_manager.get_state(device_id)
    
    if not device_data:
        print(f"   ❌ No device data found for {device_id}")
        return None, None
    
    print("   ✅ Device data loaded successfully")
    
    print_step(3, "Device data analysis")
    print(f"   Email: {device_data.get('Email', 'NOT SET')}")
    print(f"   UserName: {device_data.get('UserName', 'NOT SET')}")
    print(f"   AccountID: {device_data.get('AccountID', 'NOT SET')}")
    print(f"   Orbs: {device_data.get('Orbs', 'NOT SET')}")
    print(f"   isLinked: {device_data.get('isLinked', 'NOT SET')}")
    print(f"   synced_to_airtable: {device_data.get('synced_to_airtable', 'NOT SET')}")
    
    print_step(4, "Testing price calculation")
    orbs_value = device_data.get('Orbs', '0')
    price = calculate_price_from_orbs(orbs_value)
    print(f"   Orbs: {orbs_value} → Price: ${price}")
    
    return device_data, device_id

def test_image_path(device_name="DEVICE10", device_data=None, device_id=None):
    """Test image path generation and file existence"""
    print_header("TESTING IMAGE PATH")
    
    if device_data is None and device_id:
        device_data = device_state_manager.get_state(device_id)
    
    print_step(1, "Generating image path")
    # Use device_name for image path generation (this matches the expected format)
    image_path = get_image_path_for_device(device_name, device_data)
    print(f"   Generated path: {image_path}")
    
    print_step(2, "Checking file existence")
    if image_path and os.path.exists(image_path):
        file_size = os.path.getsize(image_path)
        print(f"   ✅ Image file exists: {image_path}")
        print(f"   File size: {file_size:,} bytes")
        return image_path
    else:
        print(f"   ❌ Image file not found: {image_path}")
        
        # Check what files are available in stock_images
        stock_dir = "stock_images"
        if os.path.exists(stock_dir):
            print(f"   Available files in {stock_dir}:")
            for file in os.listdir(stock_dir):
                print(f"     - {file}")
        return None

def test_s3_upload(image_path, device_name="DEVICE10"):
    """Test S3 image upload"""
    print_header("TESTING S3 UPLOAD")
    
    if not image_path:
        print("   ❌ No image path provided")
        return None
    
    print_step(1, "Uploading image to S3")
    image_url = upload_image_to_s3(image_path, device_name)
    
    if image_url:
        print(f"   ✅ Image uploaded successfully")
        print(f"   URL: {image_url}")
        return image_url
    else:
        print("   ❌ Image upload failed")
        return None

def test_airtable_record_lookup(email):
    """Test Airtable record lookup"""
    print_header("TESTING AIRTABLE RECORD LOOKUP")
    
    print_step(1, f"Searching for email: {email}")
    record_id = find_record_by_email(email)
    
    if record_id:
        print(f"   ✅ Record found: {record_id}")
        return record_id
    else:
        print("   ❌ No record found")
        return None

def test_full_sync(device_id):
    """Test the full sync process"""
    print_header("TESTING FULL SYNC PROCESS")
    
    print_step(1, "Running full sync")
    success = sync_device_to_airtable(device_id)
    
    if success:
        print("   ✅ Full sync completed successfully")
    else:
        print("   ❌ Full sync failed")
    
    return success

def main():
    """Main test function"""
    device_name = "DEVICE10"
    
    print_header(f"AIRTABLE SYNC TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing device: {device_name}")
    
    # Test 1: S3 Connection
    s3_ok = test_s3_connection()
    
    # Test 2: Device Data
    device_data, device_id = test_device_data(device_name)
    if not device_data or not device_id:
        print("\n❌ Cannot continue without device data")
        return
    
    # Test 3: Image Path
    image_path = test_image_path(device_name, device_data, device_id)
    
    # Test 4: S3 Upload (if image exists and S3 is working)
    if s3_ok and image_path:
        image_url = test_s3_upload(image_path, device_name)
    
    # Test 5: Airtable Record Lookup
    email = device_data.get('Email')
    if email:
        record_id = test_airtable_record_lookup(email)
    
    # Test 6: Full Sync
    print("\n" + "="*60)
    user_input = input("Do you want to run the full sync? (y/n): ").lower().strip()
    
    if user_input == 'y':
        success = test_full_sync(device_id)
        
        print_header("FINAL RESULTS")
        if success:
            print("🎉 All tests passed! Sync is working correctly.")
        else:
            print("❌ Sync failed. Check the errors above.")
    else:
        print("\n⏭️  Skipping full sync test.")
        
        print_header("TEST SUMMARY")
        print(f"✅ S3 Connection: {'OK' if s3_ok else 'FAILED'}")
        print(f"✅ Device Data: {'OK' if device_data else 'FAILED'}")
        print(f"✅ Image Path: {'OK' if image_path else 'FAILED'}")
        print(f"✅ Email Found: {'OK' if email else 'FAILED'}")

if __name__ == "__main__":
    main()
