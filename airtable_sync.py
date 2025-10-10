# airtable_sync.py - Airtable synchronization functionality
import requests
import json
import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from device_state_manager import device_state_manager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Airtable configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_ID = os.getenv('AIRTABLE_TABLE_ID')
AIRTABLE_BASE_URL = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_ID}"

# S3 Configuration
S3_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
S3_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_ACCESS_KEY')
S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
S3_REGION = os.getenv('S3_REGION')

# Global S3 client
s3_client = None

def initialize_s3():
    """Initialize S3 client with custom endpoint"""
    global s3_client
    
    if not all([S3_ACCESS_KEY_ID, S3_SECRET_ACCESS_KEY, S3_ENDPOINT, S3_BUCKET_NAME, S3_REGION]):
        print("[S3Sync] ERROR: Missing one or more required S3 environment variables.")
        return False
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=S3_ACCESS_KEY_ID,
            aws_secret_access_key=S3_SECRET_ACCESS_KEY,
            endpoint_url=f"https://{S3_ENDPOINT}",
            region_name=S3_REGION,
            config=boto3.session.Config(
                s3={'addressing_style': 'path'}  # Important for custom S3 endpoints
            )
        )
        
        # Test connection by listing buckets (or checking bucket existence)
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
        print("[S3Sync] S3 service initialized successfully.")
        return True
        
    except (ClientError, NoCredentialsError) as e:
        print(f"[S3Sync] ERROR: Initializing S3 service: {e}")
        s3_client = None
        return False

def check_and_delete_object_from_s3(s3_key, device_id):
    """Check if object exists in S3 and delete it if necessary"""
    if not s3_client:
        print(f"[{device_id}] S3 service not initialized. Skipping check/delete.")
        return False
    
    try:
        # Check if object exists
        s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        print(f"[{device_id}] Object exists in S3, deleting: {s3_key}")
        
        # Object exists, delete it
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        print(f"[{device_id}] Successfully deleted existing object from S3")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"[{device_id}] Object does not exist in S3, no need to delete")
            return False
        else:
            print(f"[{device_id}] ERROR checking/deleting S3 object: {e}")
            return False

def upload_image_to_s3(image_path, device_id):
    """Upload image to S3 and return the public URL"""
    if not s3_client:
        print(f"[{device_id}] S3 service not initialized. Skipping upload.")
        return None
    
    if not os.path.exists(image_path):
        print(f"[{device_id}] Image file not found: {image_path}")
        return None
    
    try:
        # Generate S3 key (path) for the image - no folders, direct to bucket root
        filename = os.path.basename(image_path)
        s3_key = filename
        
        # Check and delete existing object
        check_and_delete_object_from_s3(s3_key, device_id)
        
        # Upload the file with public-read ACL
        with open(image_path, 'rb') as file_data:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=s3_key,
                Body=file_data,
                ACL='public-read',
                ContentType='image/png'
            )
        
        # Generate the public URL
        image_url = f"https://{S3_ENDPOINT}/{S3_BUCKET_NAME}/{s3_key}"
        
        print(f"[{device_id}] Image uploaded to S3: {image_url}")
        return image_url
        
    except Exception as e:
        print(f"[{device_id}] Error uploading to S3: {e}")
        return None

def calculate_price_from_orbs(orbs_str):
    """Calculate price based on orbs value"""
    try:
        # Remove commas and get the first 2 digits
        orbs_clean = orbs_str.replace(",", "")
        if len(orbs_clean) >= 2:
            first_two = orbs_clean[:2]
            if first_two.startswith("20") or first_two.startswith("21"):
                return 9.99
            elif first_two.startswith("22") or first_two.startswith("23"):
                return 10.99
        return 0.00
    except:
        return 0.00

def find_record_by_email(email):
    """Find Airtable record by email"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Search for record with matching email
    params = {
        "filterByFormula": f"{{Email}} = '{email}'"
    }
    
    try:
        response = requests.get(AIRTABLE_BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        records = data.get("records", [])
        
        if records:
            return records[0]["id"]  # Return the first matching record ID
        else:
            print(f"No record found with email: {email}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error searching Airtable: {e}")
        return None

def upload_image_to_airtable(image_path, device_id):
    """Upload image file to Airtable via S3 hosting"""
    if not os.path.exists(image_path):
        print(f"[{device_id}] Image file not found: {image_path}")
        return None
    
    try:
        # Initialize S3 if not already done
        if not s3_client:
            if not initialize_s3():
                print(f"[{device_id}] Failed to initialize S3")
                return None
        
        # Upload to S3 to get a public URL
        image_url = upload_image_to_s3(image_path, device_id)
        
        if not image_url:
            print(f"[{device_id}] Failed to get S3 image URL")
            return None
        
        # Get filename for Airtable
        filename = os.path.basename(image_path)
        
        # Airtable attachment format with public URL
        attachment = [{
            "url": image_url,
            "filename": filename
        }]
        
        print(f"[{device_id}] Prepared Airtable attachment: {filename}")
        return attachment
        
    except Exception as e:
        print(f"[{device_id}] Error preparing image attachment: {e}")
        return None

def get_image_path_for_device(device_id, device_data):
    """Get the image path for a device based on new format: Stock_DeviceNumber_Username"""
    try:
        # Handle both "DEVICE10" format and IP:port format
        if device_id.startswith("DEVICE"):
            device_name = device_id
        else:
            device_name = device_state_manager._get_device_name(device_id)
        
        # Extract device number (e.g., "DEVICE10" -> "10") 
        device_number = "Unknown"
        if device_name.startswith("DEVICE"):
            device_number = device_name[6:]  # Remove "DEVICE" prefix
        
        # Get username, with smart fallback logic
        username = device_data.get("UserName", "Player")
        
        # Get current stock value
        current_stock = device_state_manager.get_current_stock()
        
        # First try with the new format: Stock_DeviceNumber_Username.png
        filename_candidate1 = f"{current_stock}_{device_number}_{username}.png"
        path_candidate1 = os.path.join("stock_images", filename_candidate1)
        
        # If that doesn't exist and username is "Player", try with AccountID
        if not os.path.exists(path_candidate1) and username == "Player":
            account_id = device_data.get("AccountID", "")
            if account_id and "ID:" in account_id:
                # Extract just the ID numbers for better naming
                id_numbers = account_id.replace("ID:", "").strip().replace(" ", "")[:6]
                username_alt = f"ID{id_numbers}"
                filename_candidate2 = f"{current_stock}_{device_number}_{username_alt}.png"
                path_candidate2 = os.path.join("stock_images", filename_candidate2)
                
                # Use AccountID-based name only if it exists
                if os.path.exists(path_candidate2):
                    username = username_alt
        
        # Try fallback to old format for backward compatibility
        if not os.path.exists(path_candidate1):
            # Check for old format: DeviceNumber_Username.png
            old_format_filename = f"{device_number}_{username}.png"
            old_format_path = os.path.join("stock_images", old_format_filename)
            if os.path.exists(old_format_path):
                print(f"[{device_id}] Found image in old format: {old_format_path}")
                return old_format_path
        
        # Construct image path with new format
        filename = f"{current_stock}_{device_number}_{username}.png"
        image_path = os.path.join("stock_images", filename)
        
        print(f"[{device_id}] Looking for image: {image_path}")
        return image_path
        
    except Exception as e:
        print(f"[{device_id}] Error getting image path: {e}")
        return None

def update_airtable_record(record_id, device_data, device_id):
    """Update Airtable record with device data"""
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    orbs_value = device_data.get("Orbs", "0")
    price = calculate_price_from_orbs(orbs_value)
    
    is_linked = device_data.get("isLinked", False)
    if isinstance(is_linked, str):
        is_linked = is_linked.lower() == "true"
    elif isinstance(is_linked, int):
        is_linked = bool(is_linked)
    
    update_data = {
        "fields": {
            "isLinked": is_linked,
            "AccountID": str(device_data.get("AccountID", "")),
            "UserName": str(device_data.get("UserName", "Player")),
            "Orbs": str(orbs_value),
            "Price": price
        }
    }
    
    # Add Gallery image
    image_path = get_image_path_for_device(device_id, device_data)
    if image_path and os.path.exists(image_path):
        gallery_attachment = upload_image_to_airtable(image_path, device_id)
        if gallery_attachment:
            update_data["fields"]["Gallery"] = gallery_attachment
            print(f"[{device_id}] Added Gallery image to sync data")
    
    try:
        url = f"{AIRTABLE_BASE_URL}/{record_id}"
        response = requests.patch(url, headers=headers, json=update_data)
        response.raise_for_status()
        
        print(f"Successfully updated Airtable record {record_id}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error updating Airtable: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return False

def sync_device_to_airtable(device_id):
    """Main function to sync device data to Airtable"""
    print(f"[{device_id}] Starting Airtable sync...")
    
    # Get device data
    device_data = device_state_manager.get_state(device_id)
    email = device_data.get("Email", "")
    
    if not email:
        print(f"[{device_id}] No email found in device data - cannot sync")
        return False
    
    print(f"[{device_id}] Searching Airtable for email: {email}")
    
    # Find record by email
    record_id = find_record_by_email(email)
    
    if not record_id:
        print(f"[{device_id}] No matching record found in Airtable")
        return False
    
    # Update the record
    success = update_airtable_record(record_id, device_data, device_id)
    
    if success:
        # Mark as synced in device state
        device_state_manager.update_state(device_id, "synced_to_airtable", True)
        print(f"[{device_id}] ✅ Airtable sync complete - marked as synced")
        return True
    else:
        print(f"[{device_id}] ❌ Airtable sync failed")
        return False

def get_device_id_from_name(device_name):
    """Convert device name (DEVICE10) to device_id (IP:port)"""
    # Reverse lookup in device_mapping
    for device_id, name in device_state_manager.device_mapping.items():
        if name == device_name:
            return device_id
    return None

# Initialize S3 when module is imported
initialize_s3()
