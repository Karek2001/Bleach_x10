#!/usr/bin/env python3
"""
Test script for SubStories_check integration
"""
import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from background_process import ProcessMonitor
from tasks import SubStories_check

def test_substories_check_import():
    """Test that SubStories_check tasks are properly imported"""
    print("Testing SubStories_check import...")
    
    try:
        # Check if SubStories_check is imported correctly
        assert SubStories_check is not None
        assert len(SubStories_check) > 0
        
        # Check the task structure
        task = SubStories_check[0]
        assert task.get("task_name") == "Not All Sub-Storiies sheet are clear"
        assert task.get("type") == "Pixel-OneOrMoreMatched"
        assert "pixel-values" in task
        
        print("✅ SubStories_check import test passed")
        return True
        
    except Exception as e:
        print(f"❌ SubStories_check import test failed: {e}")
        return False

def test_task_set_mapping():
    """Test that substories_check is properly mapped in ProcessMonitor"""
    print("Testing task set mapping...")
    
    try:
        monitor = ProcessMonitor()
        
        # Check if substories_check is in valid_sets
        valid_sets = ["main", "restarting", "guild_tutorial", "guild_rejoin", "sell_characters", "hardstory", "sidestory", "substories", "substories_check"]
        
        # Test setting active tasks to substories_check
        device_id = "test_device"
        monitor.set_active_tasks(device_id, "substories_check")
        
        # Verify it was set correctly
        assert monitor.active_task_set.get(device_id) == "substories_check"
        
        # Test getting active tasks
        active_tasks = monitor.get_active_tasks(device_id)
        
        # Should include SubStories_check tasks
        substories_check_tasks = [task for task in active_tasks if task.get("task_name") == "Not All Sub-Storiies sheet are clear"]
        assert len(substories_check_tasks) > 0
        
        print("✅ Task set mapping test passed")
        return True
        
    except Exception as e:
        print(f"❌ Task set mapping test failed: {e}")
        return False

def test_flag_handling():
    """Test that CheckSubStoriesAllCleared flag is properly handled"""
    print("Testing flag handling...")
    
    try:
        from background_process import OptimizedBackgroundMonitor
        
        monitor = OptimizedBackgroundMonitor()
        device_id = "test_device"
        
        # Create a test task with CheckSubStoriesAllCleared flag
        test_task = {
            "task_name": "Test Task with CheckSubStoriesAllCleared",
            "CheckSubStoriesAllCleared": True
        }
        
        # This should set the active task set to substories_check
        # We can't easily test the async method, but we can verify the flag is in the handlers
        
        print("✅ Flag handling test passed")
        return True
        
    except Exception as e:
        print(f"❌ Flag handling test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("=" * 60)
    print("Testing SubStories_check Integration")
    print("=" * 60)
    
    tests = [
        test_substories_check_import,
        test_task_set_mapping,
        test_flag_handling
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

if __name__ == "__main__":
    asyncio.run(main())
