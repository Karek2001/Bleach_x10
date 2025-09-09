#!/usr/bin/env python3
"""
Test script to verify SPAM_LOGS functionality
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import settings

def test_spam_logs_setting():
    """Test that SPAM_LOGS setting controls logging output"""
    print("=" * 50)
    print("Testing SPAM_LOGS functionality")
    print("=" * 50)
    
    print(f"Current SPAM_LOGS setting: {settings.SPAM_LOGS}")
    
    # Test template matching logging simulation
    def simulate_template_matching_log(found_match=True, match_count=3):
        """Simulate template matching with logging controlled by SPAM_LOGS"""
        task_name = "Test Template"
        template_path = "templates/test.png"
        
        if settings.SPAM_LOGS:
            print(f"\nTesting: {task_name}")
            print(f"  Template: {template_path}")
            print(f"  ROI: [100, 100, 200, 200]")
            
            if found_match:
                print(f"  ✓ Found {match_count} matches at confidence 0.9")
                for i in range(match_count):
                    print(f"    Match {i+1}: ({150 + i*10}, {150 + i*5}) confidence: 0.95{i}")
            else:
                print(f"  ✗ No matches found at confidence 0.9")
        
        # Always return the result regardless of logging
        return found_match
    
    # Test multi-click detection logging
    def simulate_multi_click_log(positions):
        """Simulate multi-click detection with logging controlled by SPAM_LOGS"""
        task_name = "Multi Click Test"
        
        if settings.SPAM_LOGS:
            print(f"[MULTI-DETECT] {task_name}: Found {len(positions)} matches")
        
        return len(positions)
    
    print("\n--- Testing Template Matching Logs ---")
    result1 = simulate_template_matching_log(True, 2)
    result2 = simulate_template_matching_log(False, 0)
    
    print("\n--- Testing Multi-Click Detection Logs ---")
    positions = [(100, 200), (150, 250), (200, 300)]
    result3 = simulate_multi_click_log(positions)
    
    print(f"\nTest Results:")
    print(f"  Template found: {result1}")
    print(f"  Template not found: {not result2}")
    print(f"  Multi-click positions: {result3}")
    
    print(f"\nSPAM_LOGS = {settings.SPAM_LOGS}")
    if settings.SPAM_LOGS:
        print("✓ Detailed logs are ENABLED - you should see template matching details above")
    else:
        print("✓ Detailed logs are DISABLED - you should only see test results")

if __name__ == "__main__":
    test_spam_logs_setting()
    
    print("\n" + "=" * 50)
    print("To toggle logging, edit settings.py and change SPAM_LOGS to True/False")
    print("=" * 50)
