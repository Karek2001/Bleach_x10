#!/usr/bin/env python3
# debug_startup.py - Comprehensive startup debugging tool

import sys
import traceback
import asyncio
import importlib
import os
from datetime import datetime

def print_debug(message, level="INFO"):
    """Print debug message with timestamp and level"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def test_imports():
    """Test all required imports step by step"""
    print_debug("=" * 60)
    print_debug("TESTING IMPORTS")
    print_debug("=" * 60)
    
    imports_to_test = [
        "suppress_warnings",
        "settings", 
        "device_state_manager",
        "background_process",
        "actions",
        "logical_process",
        "screenrecord_manager",
        "tasks",
        "airtable_sync"
    ]
    
    failed_imports = []
    
    for module_name in imports_to_test:
        try:
            print_debug(f"Testing import: {module_name}")
            module = importlib.import_module(module_name)
            print_debug(f"✅ {module_name} imported successfully")
            
            # Test specific attributes if they exist
            if module_name == "background_process":
                if hasattr(module, 'monitor'):
                    print_debug(f"✅ background_process.monitor found")
                else:
                    print_debug(f"⚠️  background_process.monitor NOT found", "WARNING")
                    
            if module_name == "settings":
                if hasattr(module, 'DEVICE_IDS'):
                    device_count = len(module.DEVICE_IDS)
                    print_debug(f"✅ Found {device_count} devices in settings")
                    for i, device_id in enumerate(module.DEVICE_IDS[:3]):  # Show first 3
                        print_debug(f"   Device {i+1}: {device_id}")
                    if device_count > 3:
                        print_debug(f"   ... and {device_count-3} more devices")
                else:
                    print_debug(f"❌ settings.DEVICE_IDS NOT found", "ERROR")
            
            if module_name == "tasks":
                # Test task imports
                task_sets = [
                    "StoryMode_Tasks", "Restarting_Tasks", "Shared_Tasks",
                    "Extract_Orb_Counts_Tasks", "Extract_Account_ID_Tasks",
                    "Endgame_Tasks"
                ]
                
                for task_set in task_sets:
                    if hasattr(module, task_set):
                        print_debug(f"✅ tasks.{task_set} found")
                    else:
                        print_debug(f"❌ tasks.{task_set} NOT found", "ERROR")
                        failed_imports.append(f"tasks.{task_set}")
                        
        except ImportError as e:
            print_debug(f"❌ Failed to import {module_name}: {e}", "ERROR")
            failed_imports.append(module_name)
        except Exception as e:
            print_debug(f"❌ Error testing {module_name}: {e}", "ERROR")
            print_debug(f"Traceback: {traceback.format_exc()}", "DEBUG")
            failed_imports.append(module_name)
    
    print_debug("-" * 60)
    if failed_imports:
        print_debug(f"❌ FAILED IMPORTS: {', '.join(failed_imports)}", "ERROR")
        return False
    else:
        print_debug("✅ ALL IMPORTS SUCCESSFUL", "SUCCESS")
        return True

def test_device_state_manager():
    """Test device state manager initialization"""
    print_debug("=" * 60)
    print_debug("TESTING DEVICE STATE MANAGER")
    print_debug("=" * 60)
    
    try:
        from device_state_manager import device_state_manager
        print_debug("✅ Device state manager imported")
        
        # Test getting states
        import settings
        for i, device_id in enumerate(settings.DEVICE_IDS[:2]):  # Test first 2 devices
            try:
                state = device_state_manager.get_state(device_id)
                print_debug(f"✅ Device {i+1} ({device_id}) state loaded")
                print_debug(f"   AccountID: {state.get('AccountID', 'N/A')}")
                print_debug(f"   CurrentTaskSet: {state.get('CurrentTaskSet', 'N/A')}")
                print_debug(f"   isLinked: {state.get('isLinked', 0)}")
            except Exception as e:
                print_debug(f"❌ Error loading state for {device_id}: {e}", "ERROR")
                return False
                
        return True
        
    except Exception as e:
        print_debug(f"❌ Device state manager test failed: {e}", "ERROR")
        print_debug(f"Traceback: {traceback.format_exc()}", "DEBUG")
        return False

def test_background_process():
    """Test background process initialization"""
    print_debug("=" * 60)
    print_debug("TESTING BACKGROUND PROCESS")
    print_debug("=" * 60)
    
    try:
        from background_process import monitor
        print_debug("✅ Background monitor imported")
        
        # Test monitor attributes
        if hasattr(monitor, 'process_monitor'):
            print_debug("✅ monitor.process_monitor found")
        else:
            print_debug("❌ monitor.process_monitor NOT found", "ERROR")
            return False
            
        # Test task sets
        if hasattr(monitor, 'task_sets'):
            task_count = len(monitor.task_sets)
            print_debug(f"✅ Found {task_count} task sets in monitor")
        else:
            print_debug("⚠️  monitor.task_sets not found", "WARNING")
            
        return True
        
    except Exception as e:
        print_debug(f"❌ Background process test failed: {e}", "ERROR")
        print_debug(f"Traceback: {traceback.format_exc()}", "DEBUG")
        return False

async def test_async_functions():
    """Test async functions that might be causing issues"""
    print_debug("=" * 60)
    print_debug("TESTING ASYNC FUNCTIONS")
    print_debug("=" * 60)
    
    try:
        # Test ADB command
        from actions import run_adb_command
        print_debug("Testing ADB command...")
        
        import settings
        if settings.DEVICE_IDS:
            test_device = settings.DEVICE_IDS[0]
            print_debug(f"Testing ADB connection to {test_device}")
            
            # Simple ADB test
            result = await run_adb_command("shell echo 'test'", test_device)
            if result and "test" in result:
                print_debug("✅ ADB connection working")
            else:
                print_debug(f"⚠️  ADB test result: {result}", "WARNING")
        
        return True
        
    except Exception as e:
        print_debug(f"❌ Async function test failed: {e}", "ERROR")
        print_debug(f"Traceback: {traceback.format_exc()}", "DEBUG")
        return False

def test_task_definitions():
    """Test individual task definitions for syntax errors"""
    print_debug("=" * 60)
    print_debug("TESTING TASK DEFINITIONS")
    print_debug("=" * 60)
    
    try:
        import tasks
        
        # Test specific task sets
        task_sets_to_test = [
            ("Extract_Orb_Counts_Tasks", tasks.Extract_Orb_Counts_Tasks),
            ("Extract_Account_ID_Tasks", tasks.Extract_Account_ID_Tasks),
            ("Endgame_Tasks", tasks.Endgame_Tasks),
            ("StoryMode_Tasks", tasks.StoryMode_Tasks),
            ("Restarting_Tasks", tasks.Restarting_Tasks)
        ]
        
        for task_set_name, task_set in task_sets_to_test:
            try:
                print_debug(f"Testing {task_set_name}...")
                
                if not isinstance(task_set, list):
                    print_debug(f"❌ {task_set_name} is not a list: {type(task_set)}", "ERROR")
                    continue
                
                task_count = len(task_set)
                print_debug(f"✅ {task_set_name}: {task_count} tasks")
                
                # Check first few tasks for required fields
                for i, task in enumerate(task_set[:3]):  # Check first 3 tasks
                    if not isinstance(task, dict):
                        print_debug(f"❌ Task {i+1} in {task_set_name} is not a dict", "ERROR")
                        continue
                        
                    # Check required fields
                    required_fields = ["task_name", "type"]
                    missing_fields = []
                    
                    for field in required_fields:
                        if field not in task:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        print_debug(f"❌ Task {i+1} missing: {missing_fields}", "ERROR")
                    else:
                        print_debug(f"✅ Task {i+1}: '{task.get('task_name', 'N/A')}'")
                        
            except Exception as e:
                print_debug(f"❌ Error testing {task_set_name}: {e}", "ERROR")
                
        return True
        
    except Exception as e:
        print_debug(f"❌ Task definitions test failed: {e}", "ERROR")
        print_debug(f"Traceback: {traceback.format_exc()}", "DEBUG")
        return False

async def simulate_main_startup():
    """Simulate the main.py startup process step by step"""
    print_debug("=" * 60)
    print_debug("SIMULATING MAIN.PY STARTUP")
    print_debug("=" * 60)
    
    try:
        # Step 1: Import settings
        print_debug("Step 1: Importing settings...")
        import settings
        print_debug(f"✅ Settings imported. Found {len(settings.DEVICE_IDS)} devices")
        
        # Step 2: Print device states
        print_debug("Step 2: Printing device states...")
        from device_state_manager import device_state_manager
        device_state_manager.print_all_device_states()
        print_debug("✅ Device states printed")
        
        # Step 3: Test creating monitoring tasks (without actually running them)
        print_debug("Step 3: Testing monitoring task creation...")
        from background_process import monitor
        
        device_tasks = []
        for i, device_id in enumerate(settings.DEVICE_IDS[:2]):  # Test first 2 devices only
            print_debug(f"Creating task for {device_id}")
            # Don't actually create the task, just test the function exists
            if hasattr(monitor, 'watch_device_optimized'):
                print_debug(f"✅ monitor.watch_device_optimized exists for {device_id}")
            else:
                print_debug(f"❌ monitor.watch_device_optimized NOT found", "ERROR")
                return False
        
        print_debug("✅ Monitoring task creation test passed")
        
        # Step 4: Test logical process imports
        print_debug("Step 4: Testing logical process...")
        from logical_process import run_hard_mode_swipes, handle_game_ready_routing
        print_debug("✅ Logical process functions imported")
        
        return True
        
    except Exception as e:
        print_debug(f"❌ Main startup simulation failed: {e}", "ERROR")
        print_debug(f"Traceback: {traceback.format_exc()}", "DEBUG")
        return False

def test_file_permissions():
    """Test file and directory permissions"""
    print_debug("=" * 60)
    print_debug("TESTING FILE PERMISSIONS")
    print_debug("=" * 60)
    
    files_to_check = [
        "main.py",
        "background_process.py", 
        "device_state_manager.py",
        "settings.py",
        "actions.py",
        "tasks/__init__.py",
        "tasks/extract_orb_counts.py",
        "tasks/extract_account_id.py",
        "tasks/endgame_tasks.py"
    ]
    
    for file_path in files_to_check:
        try:
            if os.path.exists(file_path):
                if os.access(file_path, os.R_OK):
                    print_debug(f"✅ {file_path} - readable")
                else:
                    print_debug(f"❌ {file_path} - NOT readable", "ERROR")
            else:
                print_debug(f"❌ {file_path} - does NOT exist", "ERROR")
        except Exception as e:
            print_debug(f"❌ Error checking {file_path}: {e}", "ERROR")

def main():
    """Main debugging function"""
    print_debug("🔧 STARTUP DEBUGGING STARTED")
    print_debug(f"Python version: {sys.version}")
    print_debug(f"Working directory: {os.getcwd()}")
    
    try:
        # Test 1: File permissions
        test_file_permissions()
        
        # Test 2: Imports
        if not test_imports():
            print_debug("❌ STOPPING: Import tests failed", "ERROR")
            return
        
        # Test 3: Device state manager
        if not test_device_state_manager():
            print_debug("❌ STOPPING: Device state manager tests failed", "ERROR")
            return
        
        # Test 4: Background process
        if not test_background_process():
            print_debug("❌ STOPPING: Background process tests failed", "ERROR")
            return
        
        # Test 5: Task definitions
        if not test_task_definitions():
            print_debug("❌ STOPPING: Task definition tests failed", "ERROR")
            return
        
        # Test 6: Async functions
        print_debug("Running async tests...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async_result = loop.run_until_complete(test_async_functions())
        if not async_result:
            print_debug("❌ STOPPING: Async function tests failed", "ERROR")
            return
        
        # Test 7: Simulate main startup
        startup_result = loop.run_until_complete(simulate_main_startup())
        if not startup_result:
            print_debug("❌ STOPPING: Main startup simulation failed", "ERROR")
            return
        
        loop.close()
        
        print_debug("=" * 60)
        print_debug("✅ ALL TESTS PASSED! The issue might be in the actual execution loop.", "SUCCESS")
        print_debug("Try running the main.py with more verbose output:")
        print_debug("python -u main.py")
        print_debug("Or check if there are any silent exceptions in the asyncio loop.")
        print_debug("=" * 60)
        
    except Exception as e:
        print_debug(f"❌ CRITICAL ERROR in debugging: {e}", "ERROR")
        print_debug(f"Traceback: {traceback.format_exc()}", "DEBUG")
    
    finally:
        print_debug("🔧 STARTUP DEBUGGING COMPLETED")

if __name__ == "__main__":
    main()
