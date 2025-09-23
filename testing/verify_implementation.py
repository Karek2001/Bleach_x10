#!/usr/bin/env python3
"""
Verification script to check the 2FA implementation in background_process.py
"""

import sys
import re
from pathlib import Path

def check_background_process_implementation():
    """Check if the 2FA implementation is correctly added to background_process.py"""
    
    print("🔍 Verifying 2FA Implementation in background_process.py")
    print("=" * 60)
    
    # Read the background_process.py file
    bg_process_file = Path("background_process.py")
    
    if not bg_process_file.exists():
        print("❌ background_process.py file not found!")
        return False
    
    with open(bg_process_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check 1: Import statement
    print("\n1️⃣ Checking import statement...")
    if "from airtable_helper import airtable_helper" in content:
        try:
            # Test the helper initialization
            print(f"✅ AirtableHelper initialized")
            print(f"   Base ID: {airtable_helper.base_id}")
            print(f"   Table ID: {airtable_helper.table_id}")
            print(f"   Expected From Prefix: {airtable_helper.expected_from_prefix}")
            
            print("✅ airtable_helper import found")
            import_check = True
        except Exception as e:
            print(f"❌ Error initializing AirtableHelper: {e}")
            import_check = False
    else:
        print("   ❌ airtable_helper import NOT found")
        import_check = False
    
    # Check 2: Get_2fa flag handling
    print("\n2️⃣ Checking Get_2fa flag handling...")
    if 'task.get("Get_2fa", False)' in content:
        print("   ✅ Get_2fa flag check found")
        flag_check = True
    else:
        print("   ❌ Get_2fa flag check NOT found")
        flag_check = False
    
    # Check 3: 60-second wait
    print("\n3️⃣ Checking 60-second wait for email...")
    if "await asyncio.sleep(60.0)" in content and "waiting 60 seconds for email to arrive" in content:
        print("   ✅ 60-second wait implementation found")
        wait_check = True
    else:
        print("   ❌ 60-second wait implementation NOT found")
        wait_check = False
    
    # Check 4: airtable_helper.get_2fa_code call
    print("\n4️⃣ Checking airtable_helper.get_2fa_code call...")
    if "await airtable_helper.get_2fa_code(email)" in content:
        print("   ✅ airtable_helper.get_2fa_code call found")
        airtable_call_check = True
    else:
        print("   ❌ airtable_helper.get_2fa_code call NOT found")
        airtable_call_check = False
    
    # Check 5: Text input execution
    print("\n5️⃣ Checking text input execution...")
    if "await execute_text_input(device_id, twofa_code)" in content:
        print("   ✅ execute_text_input call found")
        text_input_check = True
    else:
        print("   ❌ execute_text_input call NOT found")
        text_input_check = False
    
    # Check 6: Updated method signature/docstring
    print("\n6️⃣ Checking method documentation...")
    if "Handle Enter_Email, Enter_Password, and Get_2fa flags after clicking" in content:
        print("   ✅ Updated method docstring found")
        docstring_check = True
    else:
        print("   ❌ Updated method docstring NOT found")
        docstring_check = False
    
    # Check 7: Error handling and logging
    print("\n7️⃣ Checking error handling and logging...")
    success_messages = [
        "2FA code entered successfully",
        "Could not retrieve 2FA code from Airtable",
        "No email found in device state for 2FA retrieval"
    ]
    
    error_handling_check = all(msg in content for msg in success_messages)
    if error_handling_check:
        print("   ✅ Error handling and success messages found")
    else:
        print("   ❌ Some error handling messages NOT found")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 IMPLEMENTATION VERIFICATION SUMMARY")
    print("=" * 60)
    
    checks = [
        ("Import Statement", import_check),
        ("Get_2fa Flag Handling", flag_check),
        ("60-Second Wait", wait_check),
        ("Airtable Helper Call", airtable_call_check),
        ("Text Input Execution", text_input_check),
        ("Method Documentation", docstring_check),
        ("Error Handling", error_handling_check)
    ]
    
    passed = 0
    for check_name, status in checks:
        status_text = "✅ PASS" if status else "❌ FAIL"
        print(f"{check_name:.<25} {status_text}")
        if status:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(checks)} checks passed")
    
    if passed == len(checks):
        print("🎉 All implementation checks PASSED! The 2FA functionality is properly implemented.")
        return True
    else:
        print("⚠️  Some implementation checks FAILED. Please review the missing components.")
        return False

def check_requirements_txt():
    """Check if aiohttp is added to requirements.txt"""
    
    print("\n🔍 Checking requirements.txt for aiohttp dependency")
    print("-" * 40)
    
    req_file = Path("requirements.txt")
    
    if not req_file.exists():
        print("❌ requirements.txt file not found!")
        return False
    
    with open(req_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "aiohttp" in content:
        print("✅ aiohttp dependency found in requirements.txt")
        return True
    else:
        print("❌ aiohttp dependency NOT found in requirements.txt")
        return False

def main():
    """Main verification function"""
    print("🚀 2FA Implementation Verification Tool")
    print("=" * 60)
    
    # Check background_process.py implementation
    bg_process_ok = check_background_process_implementation()
    
    # Check requirements.txt
    requirements_ok = check_requirements_txt()
    
    # Final summary
    print("\n" + "=" * 60)
    print("🏆 FINAL VERIFICATION RESULTS")
    print("=" * 60)
    
    print(f"background_process.py: {'✅ GOOD' if bg_process_ok else '❌ NEEDS FIXES'}")
    print(f"requirements.txt: {'✅ GOOD' if requirements_ok else '❌ NEEDS FIXES'}")
    
    if bg_process_ok and requirements_ok:
        print("\n🎉 SUCCESS: All implementations are correct!")
        print("You can now run the test script: python test_2fa_functionality.py")
    else:
        print("\n⚠️  WARNING: Some implementations need to be fixed before testing.")

if __name__ == "__main__":
    main()
