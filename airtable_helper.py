# airtable_helper.py - Helper for Airtable 2FA code retrieval
import aiohttp
import asyncio
import re
from typing import Optional
from datetime import datetime

class AirtableHelper:
    """Helper class for retrieving 2FA codes from Airtable"""
    
    def __init__(self):
        self.api_key = "patDzdVwCMEMMBorU.aca9e4f2a36321ce580235b357a4d8a4aa1d24dc5a50f11f855d84058f084a84"
        self.base_id = "appuJAf3tqrmODVlO"
        self.table_id = "tblamaki4By1sf1Fb"
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
        params = {
            "filterByFormula": filter_formula,
            "maxRecords": 10
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, headers=headers, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"[2FA] Airtable API error: {response.status}")
                        print(f"[2FA] Error response: {error_text}")
                        print(f"[2FA] Request URL: {self.base_url}")
                        print(f"[2FA] Filter formula: {filter_formula}")
                        return None
                    
                    data = await response.json()
                    records = data.get("records", [])
                    
                    print(f"[2FA] Found {len(records)} records for email: {email}")
                    
                    # Search through records for the correct one
                    for record in records:
                        fields = record.get("fields", {})
                        original_from = fields.get("Original From", "")
                        email_content = fields.get("Email Content", "")
                        
                        # Check if this is from the expected sender (starts with prefix)
                        if not original_from.startswith(self.expected_from_prefix):
                            print(f"[2FA] Skipping record - wrong sender: {original_from}")
                            continue
                        
                        # Check if content contains verification code message
                        if "Enter the following verification" not in email_content:
                            print(f"[2FA] Skipping record - no verification text found")
                            continue
                        
                        # Extract the 6-digit code
                        code = self._extract_code(email_content)
                        if code:
                            print(f"[2FA] ✅ Successfully extracted 2FA code: {code}")
                            return code
                        else:
                            print(f"[2FA] Could not extract code from email content")
                    
                    print(f"[2FA] No valid 2FA code found in Airtable records")
                    return None
                    
        except Exception as e:
            print(f"[2FA] Error retrieving from Airtable: {e}")
            return None
    
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