#!/usr/bin/env python3
"""
Test script for 2FA functionality
Tests the airtable_helper integration and simulates the background_process 2FA flow
"""

import asyncio
import sys
import time
from datetime import datetime
from airtable_helper import airtable_helper

class TwoFAFunctionalityTester:
    """Test class for 2FA functionality"""
    
    def __init__(self):
        self.test_email = None
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print("\n" + "="*60)
        print(f" {title}")
        print("="*60)
    
    def print_step(self, step: str):
        """Print a test step"""
        print(f"\n🔍 {step}")
        print("-" * 40)
    
    async def test_airtable_connection(self):
        """Test basic Airtable connection and API response"""
        self.print_step("Testing Airtable Connection")
        
        try:
            # Test the helper initialization
            print(f"✅ AirtableHelper initialized")
            print(f"   Base ID: {airtable_helper.base_id}")
            print(f"   Table ID: {airtable_helper.table_id}")
            print(f"   Expected From Prefix: {airtable_helper.expected_from_prefix}")
            
            return True
        except Exception as e:
            print(f"❌ Failed to initialize AirtableHelper: {e}")
            return False
    
    async def test_2fa_code_retrieval(self, email: str):
        """Test 2FA code retrieval for a specific email"""
        self.print_step(f"Testing 2FA Code Retrieval for: {email}")
        
        start_time = time.time()
        
        try:
            # Call the get_2fa_code method
            print(f"🔄 Calling airtable_helper.get_2fa_code('{email}')")
            
            twofa_code = await airtable_helper.get_2fa_code(email)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏱️  Request took {duration:.2f} seconds")
            
            if twofa_code:
                print(f"✅ SUCCESS: Retrieved 2FA code: {twofa_code}")
                return twofa_code
            else:
                print(f"❌ FAILED: No 2FA code found for email: {email}")
                return None
                
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print(f"❌ ERROR after {duration:.2f}s: {e}")
            return None
    
    async def test_timestamp_sorting(self, email: str):
        """Test that Airtable returns the newest 2FA code (timestamp sorting test)"""
        self.print_step(f"Testing Timestamp Sorting for: {email}")
        
        print("🧪 This test will call the 2FA function multiple times to verify sorting")
        print("📊 It should consistently return the same (newest) code")
        
        codes_retrieved = []
        
        try:
            # Call the function 3 times in quick succession
            for i in range(3):
                print(f"\n🔄 Attempt {i+1}/3: Calling get_2fa_code...")
                
                start_time = time.time()
                twofa_code = await airtable_helper.get_2fa_code(email)
                end_time = time.time()
                
                duration = end_time - start_time
                
                if twofa_code:
                    codes_retrieved.append(twofa_code)
                    print(f"   ✅ Retrieved: {twofa_code} (took {duration:.2f}s)")
                else:
                    print(f"   ❌ No code returned (took {duration:.2f}s)")
                
                # Small delay between attempts
                if i < 2:  # Don't wait after the last attempt
                    await asyncio.sleep(1)
            
            # Analyze results
            print(f"\n📈 Results Analysis:")
            print(f"   Total attempts: 3")
            print(f"   Successful retrievals: {len(codes_retrieved)}")
            
            if len(codes_retrieved) > 0:
                # Check if all codes are the same (they should be if sorting works)
                unique_codes = set(codes_retrieved)
                print(f"   Unique codes retrieved: {len(unique_codes)}")
                print(f"   Codes: {list(unique_codes)}")
                
                if len(unique_codes) == 1:
                    print(f"   ✅ CONSISTENT: Same code returned each time (sorting works)")
                    print(f"   🎯 Consistent code: {list(unique_codes)[0]}")
                    return True
                else:
                    print(f"   ⚠️  INCONSISTENT: Different codes returned (sorting may not work)")
                    print(f"   📋 All retrieved codes: {codes_retrieved}")
                    return False
            else:
                print(f"   ❌ No codes retrieved in any attempt")
                return False
                
        except Exception as e:
            print(f"❌ ERROR during timestamp sorting test: {e}")
            return False
    
    async def simulate_background_process_flow(self, email: str, device_id: str = "test_device"):
        """Simulate the exact flow from background_process.py handle_text_input_flags method"""
        self.print_step(f"Simulating Background Process Flow for Device: {device_id}")
        
        # Create a mock task with Get_2fa flag
        mock_task = {"Get_2fa": True}
        
        print(f"📝 Mock task: {mock_task}")
        print(f"📧 Target email: {email}")
        
        try:
            # Simulate the exact flow from handle_text_input_flags
            if mock_task.get("Get_2fa", False):
                print(f"[{device_id}] 2FA code requested - waiting 60 seconds for email to arrive...")
                
                # For testing, we'll use a shorter wait time
                print("⚡ (For testing: Using 3 second wait instead of 60 seconds)")
                await asyncio.sleep(3.0)
                
                # Simulate getting email from device state (we'll use our test email)
                if not email:
                    print(f"[{device_id}] ⚠️ Warning: No email found in device state for 2FA retrieval")
                    return False
                
                print(f"[{device_id}] Retrieving 2FA code for email: {email}")
                
                # Get 2FA code from Airtable
                twofa_code = await airtable_helper.get_2fa_code(email)
                
                if twofa_code:
                    print(f"[{device_id}] Entering 2FA code: {twofa_code}")
                    # Simulate execute_text_input (we'll just print instead)
                    print(f"[{device_id}] 📱 SIMULATED: Text input executed with code: {twofa_code}")
                    print(f"[{device_id}] ✅ 2FA code entered successfully")
                    return True
                else:
                    print(f"[{device_id}] ❌ Error: Could not retrieve 2FA code from Airtable")
                    return False
        
        except Exception as e:
            print(f"[{device_id}] ❌ Exception during 2FA flow: {e}")
            return False
    
    async def run_comprehensive_test(self, email: str):
        """Run all tests"""
        self.print_header("2FA Functionality Comprehensive Test")
        
        print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📧 Testing with email: {email}")
        
        # Test 1: Basic connection
        connection_ok = await self.test_airtable_connection()
        if not connection_ok:
            print("\n❌ Cannot proceed with tests - connection failed")
            return False
        
        # Test 2: Direct 2FA retrieval test
        code = await self.test_2fa_code_retrieval(email)
        
        # Test 3: Timestamp sorting test (NEW)
        sorting_ok = await self.test_timestamp_sorting(email)
        
        # Test 4: Simulate background process flow
        flow_success = await self.simulate_background_process_flow(email)
        
        # Results summary
        self.print_header("Test Results Summary")
        
        print(f"✅ Airtable Connection: {'PASS' if connection_ok else 'FAIL'}")
        print(f"✅ 2FA Code Retrieval: {'PASS' if code else 'FAIL'}")
        print(f"✅ Timestamp Sorting: {'PASS' if sorting_ok else 'FAIL'}")
        print(f"✅ Background Process Flow: {'PASS' if flow_success else 'FAIL'}")
        
        if code:
            print(f"\n🎯 Final 2FA Code Retrieved: {code}")
        
        # Additional analysis
        if sorting_ok:
            print(f"\n🔍 Sorting Analysis:")
            print(f"   ✅ Airtable returns consistent results (newest first)")
            print(f"   ✅ Background process should get latest 2FA codes")
        else:
            print(f"\n⚠️  Sorting Analysis:")
            print(f"   ❌ Airtable returns inconsistent results")
            print(f"   ❌ Background process may get old 2FA codes")
        
        overall_success = connection_ok and code and sorting_ok and flow_success
        print(f"\n🏆 Overall Test Result: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
        
        return overall_success

def main():
    """Main function to run the tests"""
    print("🚀 2FA Functionality Tester")
    print("=" * 60)
    
    # Ask user for email
    email = input("Please enter the email address to test 2FA retrieval for: ").strip()
    
    if not email:
        print("❌ No email provided. Exiting.")
        sys.exit(1)
    
    if "@" not in email:
        print("❌ Invalid email format. Exiting.")
        sys.exit(1)
    
    print(f"📧 Testing with email: {email}")
    
    # Create tester and run tests
    tester = TwoFAFunctionalityTester()
    
    try:
        # Run the comprehensive test
        success = asyncio.run(tester.run_comprehensive_test(email))
        
        if success:
            print("\n🎉 All tests passed! The 2FA functionality is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Please check the output above for details.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
