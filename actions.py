# actions.py - Enhanced Version with Smart Multi-Detection and Anti-Spam
import asyncio
import subprocess
import io
import time
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import os
from collections import defaultdict

import numpy as np
from PIL import Image
import cv2
from screenrecord_manager import get_screenrecord_manager, cleanup_all_screenrecord

# PyAutoGUI import with headless environment handling
try:
    import pyautogui
    pyautogui.FAILSAFE = False
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    print("[MATCHING] PyAutoGUI not available - using OpenCV fallback")
    PYAUTOGUI_AVAILABLE = False
except Exception as e:
    print(f"[MATCHING] PyAutoGUI import issue: {e}")
    PYAUTOGUI_AVAILABLE = False

# --- Screenshot Cache ---
@dataclass
class ScreenshotCache:
    """Caches screenshots to avoid redundant captures"""
    image: np.ndarray
    timestamp: float
    
class ScreenshotManager:
    def __init__(self, cache_duration: float = 0.1):
        self.cache: Dict[str, ScreenshotCache] = {}
        self.cache_duration = cache_duration
        self.locks: Dict[str, asyncio.Lock] = {}
        self.streaming_enabled = False
    
    async def get_screenshot(self, device_id: str) -> Optional[np.ndarray]:
        """Get screenshot using ADB screencap with caching"""
        if device_id not in self.locks:
            self.locks[device_id] = asyncio.Lock()
        
        async with self.locks[device_id]:
            current_time = time.time()
            
            # Check cache
            if device_id in self.cache:
                cached = self.cache[device_id]
                if current_time - cached.timestamp < self.cache_duration:
                    return cached.image
            
            img = await self._capture_screenshot_adb(device_id)
            
            if img is not None:
                self.cache[device_id] = ScreenshotCache(img, current_time)
            return img
    
    async def _capture_screenshot_adb(self, device_id: str) -> Optional[np.ndarray]:
        """Capture screenshot using ADB (fallback)"""
        try:
            command = f"adb -s {device_id} exec-out screencap -p"
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if not stdout:
                return None
            
            pil_image = Image.open(io.BytesIO(stdout)).convert('RGB')
            return np.asarray(pil_image)
            
        except Exception as e:
            print(f"ADB screenshot failed for {device_id}: {e}")
            return None

# Global screenshot manager
screenshot_manager = ScreenshotManager()

# --- Template Cache ---
class TemplateCache:
    """Cache for template images to avoid repeated loading"""
    def __init__(self):
        self.templates: Dict[str, np.ndarray] = {}
        self.cache_size_limit = 50
    
    def get_template(self, template_path: str) -> Optional[np.ndarray]:
        """Load and cache template image"""
        if template_path in self.templates:
            return self.templates[template_path]
        
        if not os.path.exists(template_path):
            print(f"Template not found: {template_path}")
            return None
        
        try:
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                return None
            
            template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
            
            if len(self.templates) >= self.cache_size_limit:
                self.templates.pop(next(iter(self.templates)))
            
            self.templates[template_path] = template
            return template
        except Exception as e:
            print(f"Error loading template {template_path}: {e}")
            return None

template_cache = TemplateCache()

# --- Enhanced Task Execution Tracker ---
class TaskExecutionTracker:
    """Advanced tracker to prevent task spam and manage execution timing"""
    def __init__(self):
        self.last_execution: Dict[str, Dict[str, float]] = {}  # device_id -> {task_name: timestamp}
        self.execution_count: Dict[str, Dict[str, int]] = {}  # device_id -> {task_name: count}
        self.cooldowns: Dict[str, float] = {}  # task_name -> cooldown_seconds
        self.frame_tasks: Dict[str, Set[str]] = {}  # device_id -> set of tasks executed this frame
        self.last_frame_time: Dict[str, float] = {}  # device_id -> timestamp
        
    def set_task_cooldown(self, task_name: str, cooldown: float):
        """Set cooldown for a specific task"""
        self.cooldowns[task_name] = cooldown
    
    def can_execute_task(self, device_id: str, task_name: str, 
                         default_cooldown: float = 2.0) -> bool:
        """Check if task can be executed based on cooldowns and frame limits"""
        current_time = time.time()
        
        # Initialize device tracking if needed
        if device_id not in self.last_execution:
            self.last_execution[device_id] = {}
            self.execution_count[device_id] = {}
            self.frame_tasks[device_id] = set()
            self.last_frame_time[device_id] = 0
        
        # Reset frame tracking if this is a new frame (>100ms since last frame)
        if current_time - self.last_frame_time[device_id] > 0.1:
            self.frame_tasks[device_id] = set()
            self.last_frame_time[device_id] = current_time
        
        # Check if task was already executed in this frame
        if task_name in self.frame_tasks[device_id]:
            return False
        
        # Check cooldown
        last_time = self.last_execution[device_id].get(task_name, 0)
        cooldown = self.cooldowns.get(task_name, default_cooldown)
        
        if current_time - last_time < cooldown:
            return False
        
        return True
    
    def record_execution(self, device_id: str, task_name: str):
        """Record that a task was executed"""
        current_time = time.time()
        
        if device_id not in self.last_execution:
            self.last_execution[device_id] = {}
            self.execution_count[device_id] = {}
            self.frame_tasks[device_id] = set()
        
        self.last_execution[device_id][task_name] = current_time
        self.execution_count[device_id][task_name] = \
            self.execution_count[device_id].get(task_name, 0) + 1
        self.frame_tasks[device_id].add(task_name)
    
    def get_execution_count(self, device_id: str, task_name: str) -> int:
        """Get how many times a task has been executed"""
        if device_id not in self.execution_count:
            return 0
        return self.execution_count[device_id].get(task_name, 0)

# Global task tracker
task_tracker = TaskExecutionTracker()

# --- Smart Template Matching Functions ---
async def find_all_templates_smart(screenshot: np.ndarray, 
                                  templates_to_check: List[Tuple[str, Tuple[int, int, int, int], float]],
                                  min_distance: int = 30) -> Dict[str, List[Tuple[int, int]]]:
    """
    Find all instances of multiple templates in a single screenshot.
    Returns dict of template_path -> list of (x, y) positions
    """
    all_matches = {}
    
    for template_path, roi, confidence in templates_to_check:
        try:
            template = template_cache.get_template(template_path)
            if template is None:
                continue
            
            # Extract ROI
            x, y, w, h = roi
            roi_img = screenshot[y:y+h, x:x+w]
            
            if roi_img.size == 0:
                continue
            
            # Perform template matching
            result = cv2.matchTemplate(roi_img.astype(np.uint8), 
                                     template.astype(np.uint8), 
                                     cv2.TM_CCOEFF_NORMED)
            
            # Find all matches above confidence
            locations = np.where(result >= confidence)
            
            if len(locations[0]) == 0:
                continue
            
            matches = []
            template_h, template_w = template.shape[:2]
            
            # Convert to center points and filter duplicates
            for pt_y, pt_x in zip(locations[0], locations[1]):
                center_x = x + pt_x + template_w // 2
                center_y = y + pt_y + template_h // 2
                
                # Check for duplicates
                is_duplicate = False
                for existing_x, existing_y in matches:
                    dist_sq = (center_x - existing_x)**2 + (center_y - existing_y)**2
                    if dist_sq < min_distance**2:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    matches.append((center_x, center_y))
            
            if matches:
                all_matches[template_path] = matches
                
        except Exception as e:
            print(f"Error matching template {template_path}: {e}")
            continue
    
    return all_matches

async def batch_check_pixels_enhanced(device_id: str, tasks: List[dict], 
                                     screenshot: Optional[np.ndarray] = None) -> List[dict]:
    """Enhanced batch checking with smart multi-detection and anti-spam"""
    if screenshot is not None:
        img_gpu = screenshot
    else:
        img_gpu = await screenshot_manager.get_screenshot(device_id)
    
    if img_gpu is None:
        return []
    
    # Separate tasks by detection type
    pixel_tasks = []
    template_tasks = []
    shared_detection_tasks = []
    
    for task in tasks:
        task_type = task.get("type", "pixel")
        
        if task_type == "pixel":
            pixel_tasks.append(task)
        elif task_type == "template":
            if task.get("shared_detection", False):
                shared_detection_tasks.append(task)
            else:
                template_tasks.append(task)
    
    matched_tasks = []
    
    # Process pixel tasks (original logic)
    for task in pixel_tasks:
        search_array = task["search_array"]
        all_match = True
        
        for i in range(0, len(search_array), 2):
            coords_str, hex_color = search_array[i], search_array[i+1]
            x, y = map(int, coords_str.split(','))
            
            expected_rgb = hex_to_rgb(hex_color)
            expected_rgb_gpu = np.array(expected_rgb)
            
            if 0 <= y < img_gpu.shape[0] and 0 <= x < img_gpu.shape[1]:
                pixel_color_gpu = img_gpu[y, x]
                if not np.array_equal(pixel_color_gpu, expected_rgb_gpu):
                    all_match = False
                    break
            else:
                all_match = False
                break
        
        if all_match:
            # Check if we can execute this task (cooldown/spam prevention)
            if task_tracker.can_execute_task(device_id, task["task_name"]):
                matched_tasks.append(task)
    
    # Process shared detection templates (all at once)
    if shared_detection_tasks:
        templates_to_check = []
        task_map = {}
        
        for task in shared_detection_tasks:
            template_paths = task.get("template_paths", [])
            if task.get("template_path"):
                template_paths = [task["template_path"]]
            
            roi = task.get("roi", [0, 0, img_gpu.shape[1], img_gpu.shape[0]])
            confidence = task.get("confidence", 0.9)
            
            for template_path in template_paths:
                templates_to_check.append((template_path, roi, confidence))
                task_map[template_path] = task
        
        # Find all matches in single pass
        all_matches = await find_all_templates_smart(img_gpu, templates_to_check)
        
        # Process matches by priority
        for template_path, positions in all_matches.items():
            task = task_map[template_path]
            task_name = task["task_name"]
            
            # Check if we can execute this task
            if not task_tracker.can_execute_task(device_id, task_name):
                continue
            
            # Handle multi-click tasks
            if task.get("multi_click", False) or "UnClear" in task_name:
                print(f"[MULTI-DETECT] {task_name}: Found {len(positions)} matches")
                for i, (x, y) in enumerate(positions):
                    await execute_tap(device_id, f"{x},{y}")
                    await asyncio.sleep(0.10)
                
                task_tracker.record_execution(device_id, task_name)
                task_copy = task.copy()
                task_copy["task_name"] = f"{task_name} [Multi: {len(positions)} clicks]"
                matched_tasks.append(task_copy)
            else:
                # Single click task - use first match
                if positions:
                    x, y = positions[0]
                    task_copy = task.copy()
                    task_copy["click_location_str"] = f"{x},{y}"
                    task_copy["use_match_position"] = True
                    matched_tasks.append(task_copy)
                    task_tracker.record_execution(device_id, task_name)
    
    # Process regular template tasks (one by one, with anti-spam)
    for task in template_tasks:
        task_name = task["task_name"]
        
        # Skip if task was recently executed
        if not task_tracker.can_execute_task(device_id, task_name):
            continue
        
        template_paths = task.get("template_paths", [])
        if task.get("template_path"):
            template_paths = [task["template_path"]]
        
        roi = task.get("roi", [0, 0, img_gpu.shape[1], img_gpu.shape[0]])
        confidence = task.get("confidence", 0.9)
        
        match_found = False
        for template_path in template_paths:
            match_pos = await find_template_in_region(img_gpu, template_path, roi, confidence)
            if match_pos:
                task_copy = task.copy()
                if task.get("use_match_position", False):
                    task_copy["click_location_str"] = f"{match_pos[0]},{match_pos[1]}"
                matched_tasks.append(task_copy)
                task_tracker.record_execution(device_id, task_name)
                match_found = True
                break
        
        if match_found:
            break  # Stop after first regular template match
    
    return matched_tasks

# Helper functions
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Converts a hex color string to an (R, G, B) tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

async def run_adb_command(command: str, device_id: Optional[str] = None) -> bytes:
    """Optimized ADB command execution"""
    full_command = f"adb -s {device_id} {command}" if device_id else f"adb {command}"
    
    process = await asyncio.create_subprocess_shell(
        full_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    stdout, stderr = await process.communicate()
    return stdout

async def execute_tap(device_id: str, location_str: str):
    """Execute tap command asynchronously"""
    coords = location_str.replace(',', ' ')
    await run_adb_command(f"shell input tap {coords}", device_id)

async def find_template_in_region(screenshot: np.ndarray, template_path: str, 
                                 roi: Tuple[int, int, int, int], 
                                 confidence: float = 0.9) -> Optional[Tuple[int, int]]:
    """Find template in a specific region of the screenshot."""
    try:
        template = template_cache.get_template(template_path)
        if template is None:
            return None
        
        x, y, w, h = roi
        roi_img = screenshot[y:y+h, x:x+w]
        
        if roi_img.size == 0:
            return None
        
        result = cv2.matchTemplate(roi_img.astype(np.uint8), 
                                  template.astype(np.uint8), 
                                  cv2.TM_CCOEFF_NORMED)
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            template_h, template_w = template.shape[:2]
            center_x = x + max_loc[0] + template_w // 2
            center_y = y + max_loc[1] + template_h // 2
            return (center_x, center_y)
        
        return None
        
    except Exception as e:
        print(f"Template matching error: {e}")
        return None

# Configure default cooldowns for common task types
task_tracker.set_task_cooldown("Click [Skip]", 3.0)
task_tracker.set_task_cooldown("Connection Error - Retry", 5.0)
task_tracker.set_task_cooldown("Click [OK]", 2.0)

# Export the enhanced batch check function with the original name for compatibility
batch_check_pixels = batch_check_pixels_enhanced