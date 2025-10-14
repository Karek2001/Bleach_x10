# airtable_helper.py - Helper for Airtable 2FA code retrieval
import aiohttp
import asyncio
import re
import os
import ssl
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AirtableHelper:
    """Helper class for retrieving 2FA codes from Airtable"""
    
    def __init__(self):
        self.api_key = os.getenv('AIRTABLE_API_KEY')
        self.base_id = os.getenv('AIRTABLE_2FA_BASE_ID')
        self.table_id = os.getenv('AIRTABLE_2FA_TABLE_ID')
        self.base_url = f"https://api.airtable.com/v0/{self.base_id}/{self.table_id}"
        self.expected_from_prefix = "noreply_at_id_klabgames_net"
    
    async def get_2fa_code(self, email: str) -> Optional[str]:
        """Retrieve 2FA code from Airtable for the given email"""
        print(f"[2FA] Searching Airtable for 2FA code for email: {email}")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Build filter formula to find matching records
        filter_formula = f"{{Original To}}='{email}'"
        
        # Try different Airtable system field names for sorting
        sort_field_names = ["LAST_MODIFIED_TIME", "CREATED_TIME", "lastModifiedTime", "createdTime"]
        
        data = None
        
        # Create SSL context that doesn't verify certificates (for Windows SSL issues)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Try each sort field until one works
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context)) as session:
            for field_name in sort_field_names:
                params = {
                    "filterByFormula": filter_formula,
                    "maxRecords": 10,
                    "sort[0][field]": field_name,
                    "sort[0][direction]": "desc"
                }
                
                print(f"[2FA] Trying sort field: {field_name}")
                
                try:
                    async with session.get(self.base_url, headers=headers, params=params) as response:
                        if response.status == 200:
                            print(f"[2FA] ✅ Success with field: {field_name}")
                            data = await response.json()
                            break
                        else:
                            error_text = await response.text()
                            if "UNKNOWN_FIELD_NAME" in error_text:
                                print(f"[2FA] Field '{field_name}' not found, trying next...")
                                continue
                            else:
                                print(f"[2FA] Unexpected error: {response.status} - {error_text}")
                                return None
                except Exception as e:
                    print(f"[2FA] Exception with field '{field_name}': {e}")
                    continue
            
            # If all sort fields failed, try without sorting
            if data is None:
                print(f"[2FA] All sort fields failed, trying without sorting...")
                params = {
                    "filterByFormula": filter_formula,
                    "maxRecords": 10
                }
                
                try:
                    async with session.get(self.base_url, headers=headers, params=params) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            print(f"[2FA] Final fallback failed: {response.status} - {error_text}")
                            return None
                        data = await response.json()
                except Exception as e:
                    print(f"[2FA] Final fallback exception: {e}")
                    return None
        
        if not data:
            return None
            
        records = data.get("records", [])
        print(f"[2FA] Found {len(records)} records for email: {email}")
        
        # Debug: Show what fields are available in the first record
        if records:
            first_record = records[0]
            print(f"[2FA] DEBUG - Available fields in record: {list(first_record.keys())}")
            if 'createdTime' in first_record:
                print(f"[2FA] DEBUG - Record createdTime: {first_record['createdTime']}")
            if 'fields' in first_record:
                print(f"[2FA] DEBUG - Available field names: {list(first_record['fields'].keys())}")
        
        # Try to manually sort records by createdTime if available
        valid_records = []
        
        # First pass: collect valid 2FA records
        for i, record in enumerate(records):
            fields = record.get("fields", {})
            original_from = fields.get("Original From", "")
            email_content = fields.get("Email Content", "")
            created_time = record.get("createdTime", "")
            
            print(f"[2FA] Record {i+1}: createdTime={created_time}, sender={original_from[:30]}...")
            
            # Check if this is from the expected sender
            if not original_from.startswith(self.expected_from_prefix):
                print(f"[2FA] Skipping record {i+1} - wrong sender")
                continue
            
            # Check if content contains verification code message
            if "Enter the following verification" not in email_content:
                print(f"[2FA] Skipping record {i+1} - no verification text found")
                continue
            
            # Extract the 6-digit code
            code = self._extract_code(email_content)
            if code:
                valid_records.append({
                    'record': record,
                    'code': code,
                    'created_time': created_time
                })
                print(f"[2FA] Valid record {i+1}: code={code}, time={created_time}")
        
        if not valid_records:
            print(f"[2FA] No valid 2FA records found")
            return None
        
        # Sort valid records by createdTime (newest first) if createdTime is available
        if valid_records[0]['created_time']:
            print(f"[2FA] Sorting {len(valid_records)} valid records by createdTime...")
            valid_records.sort(key=lambda x: x['created_time'], reverse=True)
            
            for i, vr in enumerate(valid_records):
                print(f"[2FA] Sorted record {i+1}: code={vr['code']}, time={vr['created_time']}")
        else:
            print(f"[2FA] No createdTime available, using first valid record")
        
        # Return the code from the newest (first) record
        selected_code = valid_records[0]['code']
        selected_time = valid_records[0]['created_time'] 
        print(f"[2FA] ✅ Selected code: {selected_code} (time: {selected_time})")
        return selected_code
    
    def _extract_code(self, email_content: str) -> Optional[str]:
        """Extract 6-digit verification code from email content"""
        # Look for a standalone 6-digit number
        # Pattern: word boundary, 6 digits, word boundary
        pattern = r'\b(\d{6})\b'
        
        matches = re.findall(pattern, email_content)
        
        if matches:
            # Return the first 6-digit code found
            code = matches[0]
            print(f"[2FA] Extracted code from email: {code}")
            return code
        
        # Alternative: Look for numbers with 3+ digits if 6-digit not found
        pattern_alt = r'\b(\d{3,})\b'
        matches_alt = re.findall(pattern_alt, email_content)
        
        for match in matches_alt:
            if len(match) >= 3:
                print(f"[2FA] Extracted alternative code: {match}")
                return match
        
        return None

# Global instance
airtable_helper = AirtableHelper()