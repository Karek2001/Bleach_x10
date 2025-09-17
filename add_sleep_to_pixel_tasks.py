#!/usr/bin/env python3
"""
Script to add 'sleep': 3 to all pixel type tasks across all task files
"""

import os
import re
import glob

def add_sleep_to_pixel_tasks():
    """Add sleep: 3 to all pixel type tasks in all task files"""
    
    tasks_dir = "tasks"
    modified_files = []
    
    # Get all Python files in tasks directory
    task_files = glob.glob(os.path.join(tasks_dir, "*.py"))
    
    for file_path in task_files:
        if "__init__.py" in file_path or "__pycache__" in file_path:
            continue
            
        print(f"Processing {file_path}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Pattern to match pixel task blocks
            # This matches from "type": "pixel" to the closing brace of the task
            pixel_task_pattern = r'(\{\s*\n(?:[^{}]*\n)*?\s*"type":\s*"pixel"[^{}]*?)(\n\s*\},?)'
            
            def add_sleep_to_match(match):
                task_block = match.group(1)
                closing = match.group(2)
                
                # Check if task already has sleep parameter
                if '"sleep"' in task_block:
                    return match.group(0)  # Return unchanged if sleep already exists
                
                # Find the last property before the closing brace
                # Look for patterns like: "property": value,
                last_prop_pattern = r'(\n\s*"[^"]+"\s*:\s*[^,\n]+),?(\s*)$'
                last_prop_match = re.search(last_prop_pattern, task_block)
                
                if last_prop_match:
                    # Add comma to last property if not present, then add sleep
                    last_prop = last_prop_match.group(1)
                    if not last_prop.endswith(','):
                        last_prop += ','
                    
                    spacing = last_prop_match.group(2) if last_prop_match.group(2) else '\n        '
                    sleep_line = f'{spacing}"sleep": 3,'
                    
                    # Replace the last property with the last property + sleep
                    task_block = task_block[:last_prop_match.start()] + last_prop + sleep_line + task_block[last_prop_match.end():]
                
                return task_block + closing
            
            # Apply the transformation
            modified_content = re.sub(pixel_task_pattern, add_sleep_to_match, content, flags=re.MULTILINE | re.DOTALL)
            
            # Check if any changes were made
            if modified_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                modified_files.append(file_path)
                print(f"  ✓ Modified {file_path}")
            else:
                print(f"  - No changes needed for {file_path}")
                
        except Exception as e:
            print(f"  ✗ Error processing {file_path}: {e}")
    
    print(f"\nCompleted! Modified {len(modified_files)} files:")
    for file_path in modified_files:
        print(f"  - {file_path}")

if __name__ == "__main__":
    add_sleep_to_pixel_tasks()
