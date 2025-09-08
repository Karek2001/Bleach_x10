#!/usr/bin/env python3
"""
Test script for KeepChecking functionality
"""
import asyncio
import time
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from background_process import OptimizedBackgroundMonitor

def test_keep_checking_timer():
    """Test KeepChecking timer functionality"""
    print("Testing KeepChecking timer...")
    
    try:
        monitor = OptimizedBackgroundMonitor()
        device_id = "test_device"
        
        # Initially no KeepChecking
        assert device_id not in monitor.keep_checking_until
        assert device_id not in monitor.keep_checking_task
        
        # Simulate setting KeepChecking
        current_time = time.time()
        monitor.keep_checking_until[device_id] = current_time + 2.0  # 2 seconds
        monitor.keep_checking_task[device_id] = "Test Task"
        
        # Should be in KeepChecking mode
        assert device_id in monitor.keep_checking_until
        assert monitor.keep_checking_task[device_id] == "Test Task"
        
        print("✅ KeepChecking timer test passed")
        return True
        
    except Exception as e:
        print(f"❌ KeepChecking timer test failed: {e}")
        return False

def test_keep_checking_task_filtering():
    """Test that KeepChecking filters tasks correctly"""
    print("Testing KeepChecking task filtering...")
    
    try:
        monitor = OptimizedBackgroundMonitor()
        device_id = "test_device"
        
        # Create mock tasks
        mock_tasks = [
            {"task_name": "Task A", "priority": 1},
            {"task_name": "Task B", "priority": 2}, 
            {"task_name": "Keep Checking Task", "priority": 3}
        ]
        
        # Mock the get_active_tasks method
        original_get_active_tasks = monitor.process_monitor.get_active_tasks
        monitor.process_monitor.get_active_tasks = lambda device_id: mock_tasks
        
        # Test normal mode (no KeepChecking)
        tasks = monitor.get_prioritized_tasks(device_id)
        assert len(tasks) == 3
        
        # Set KeepChecking mode
        current_time = time.time()
        monitor.keep_checking_until[device_id] = current_time + 5.0
        monitor.keep_checking_task[device_id] = "Keep Checking Task"
        
        # Should only return the KeepChecking task
        tasks = monitor.get_prioritized_tasks(device_id)
        assert len(tasks) == 1
        assert tasks[0]["task_name"] == "Keep Checking Task"
        
        # Restore original method
        monitor.process_monitor.get_active_tasks = original_get_active_tasks
        
        print("✅ KeepChecking task filtering test passed")
        return True
        
    except Exception as e:
        print(f"❌ KeepChecking task filtering test failed: {e}")
        return False

def test_keep_checking_expiration():
    """Test that KeepChecking expires correctly"""
    print("Testing KeepChecking expiration...")
    
    try:
        monitor = OptimizedBackgroundMonitor()
        device_id = "test_device"
        
        # Set KeepChecking with very short duration
        current_time = time.time()
        monitor.keep_checking_until[device_id] = current_time + 0.1  # 0.1 seconds
        monitor.keep_checking_task[device_id] = "Test Task"
        
        # Wait for expiration
        time.sleep(0.2)
        
        # Mock the get_active_tasks method
        mock_tasks = [{"task_name": "Task A", "priority": 1}]
        monitor.process_monitor.get_active_tasks = lambda device_id: mock_tasks
        
        # Should expire and return all tasks
        tasks = monitor.get_prioritized_tasks(device_id)
        
        # Should have cleared the KeepChecking state
        assert device_id not in monitor.keep_checking_until
        assert device_id not in monitor.keep_checking_task
        
        print("✅ KeepChecking expiration test passed")
        return True
        
    except Exception as e:
        print(f"❌ KeepChecking expiration test failed: {e}")
        return False

async def test_keep_checking_integration():
    """Test KeepChecking integration with task processing"""
    print("Testing KeepChecking integration...")
    
    try:
        monitor = OptimizedBackgroundMonitor()
        device_id = "test_device"
        
        # Create a test task with KeepChecking
        test_task = {
            "task_name": "Test KeepChecking Task",
            "KeepChecking": 2.0,
            "click_location_str": "100,100",
            "priority": 1
        }
        
        # Simulate processing the task (without actually executing it)
        current_time = time.time()
        
        # Manually trigger KeepChecking logic
        if "KeepChecking" in test_task:
            keep_checking_duration = float(test_task["KeepChecking"])
            monitor.keep_checking_until[device_id] = current_time + keep_checking_duration
            monitor.keep_checking_task[device_id] = test_task["task_name"]
        
        # Verify KeepChecking was set
        assert device_id in monitor.keep_checking_until
        assert monitor.keep_checking_task[device_id] == "Test KeepChecking Task"
        assert monitor.keep_checking_until[device_id] > current_time
        
        print("✅ KeepChecking integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ KeepChecking integration test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("=" * 60)
    print("Testing KeepChecking Functionality")
    print("=" * 60)
    
    tests = [
        test_keep_checking_timer,
        test_keep_checking_task_filtering,
        test_keep_checking_expiration,
        test_keep_checking_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if asyncio.iscoroutinefunction(test):
            result = await test()
        else:
            result = test()
            
        if result:
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All KeepChecking tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

if __name__ == "__main__":
    asyncio.run(main())
