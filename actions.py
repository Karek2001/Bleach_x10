# actions.py - Enhanced Version with OCR Support
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
import settings

# OCR imports
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    # Configure Tesseract path for Windows (adjust as needed)
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
except ImportError:
    print("[OCR] Tesseract not available - OCR features disabled")
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    # Initialize EasyOCR reader (supports multiple languages)
    ocr_reader = easyocr.Reader(['en'], gpu=True)  # Use GPU if available
    EASYOCR_AVAILABLE = True
except ImportError:
    print("[OCR] EasyOCR not available - falling back to Tesseract")
    EASYOCR_AVAILABLE = False
    ocr_reader = None

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
            if settings.SPAM_LOGS:
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
            if settings.SPAM_LOGS:
                print(f"Error loading template {template_path}: {e}")
            return None

template_cache = TemplateCache()

# --- OCR Functions ---
class OCRManager:
    """Manages OCR operations with caching and optimization"""
    
    def __init__(self):
        self.ocr_cache: Dict[str, Dict] = {}  # Cache OCR results
        self.cache_duration = 0.5  # OCR cache duration in seconds
        
    async def extract_text_from_region(self, screenshot: np.ndarray, 
                                      roi: Tuple[int, int, int, int],
                                      use_easyocr: bool = True) -> List[Tuple[str, Tuple[int, int]]]:
        """
        Extract text from a specific region of the screenshot.
        Returns list of (text, center_position) tuples.
        """
        x, y, w, h = roi
        roi_img = screenshot[y:y+h, x:x+w]
        
        if roi_img.size == 0:
            return []
        
        detected_texts = []
        
        try:
            if use_easyocr and EASYOCR_AVAILABLE:
                # Use EasyOCR for better accuracy
                results = ocr_reader.readtext(roi_img, detail=1)
                
                for (bbox, text, confidence) in results:
                    if confidence > 0.5:  # Filter low confidence
                        # Calculate center position
                        min_x = min(pt[0] for pt in bbox)
                        max_x = max(pt[0] for pt in bbox)
                        min_y = min(pt[1] for pt in bbox)
                        max_y = max(pt[1] for pt in bbox)
                        
                        center_x = x + (min_x + max_x) // 2
                        center_y = y + (min_y + max_y) // 2
                        
                        detected_texts.append((text.lower(), (center_x, center_y)))
                        
            elif TESSERACT_AVAILABLE:
                # Use Tesseract as fallback
                # Preprocess image for better OCR
                gray = cv2.cvtColor(roi_img, cv2.COLOR_RGB2GRAY)
                
                # Apply threshold to get black text on white background
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # Get OCR data with positions
                data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
                
                for i in range(len(data['text'])):
                    text = data['text'][i].strip().lower()
                    conf = int(data['conf'][i])
                    
                    if text and conf > 50:  # Filter empty and low confidence
                        box_x = data['left'][i]
                        box_y = data['top'][i]
                        box_w = data['width'][i]
                        box_h = data['height'][i]
                        
                        center_x = x + box_x + box_w // 2
                        center_y = y + box_y + box_h // 2
                        
                        detected_texts.append((text, (center_x, center_y)))
            
        except Exception as e:
            print(f"OCR error: {e}")
        
        return detected_texts
    
    async def find_text_in_region(self, screenshot: np.ndarray,
                                 search_texts: List[str],
                                 roi: Tuple[int, int, int, int]) -> Optional[Tuple[str, Tuple[int, int]]]:
        """
        Find any of the search texts in the specified region.
        Returns (matched_text, position) or None.
        """
        detected_texts = await self.extract_text_from_region(screenshot, roi)
        
        for search_text in search_texts:
            search_lower = search_text.lower().strip()
            
            for detected_text, position in detected_texts:
                # Check for exact match or substring match
                if search_lower in detected_text or detected_text in search_lower:
                    return (search_text, position)
        
        return None

# Global OCR manager
ocr_manager = OCRManager()

# --- Enhanced Task Execution Tracker ---
class TaskExecutionTracker:
    """Advanced tracker to prevent task spam and manage execution timing"""
    def __init__(self):
        self.last_execution: Dict[str, Dict[str, float]] = {}
        self.execution_count: Dict[str, Dict[str, int]] = {}
        self.cooldowns: Dict[str, float] = {}
        self.frame_tasks: Dict[str, Set[str]] = {}
        self.last_frame_time: Dict[str, float] = {}
        
    def set_task_cooldown(self, task_name: str, cooldown: float):
        """Set cooldown for a specific task"""
        self.cooldowns[task_name] = cooldown
    
    def can_execute_task(self, device_id: str, task_name: str, 
                         default_cooldown: float = 2.0) -> bool:
        """Check if task can be executed based on cooldowns and frame limits"""
        current_time = time.time()
        
        if device_id not in self.last_execution:
            self.last_execution[device_id] = {}
            self.execution_count[device_id] = {}
            self.frame_tasks[device_id] = set()
            self.last_frame_time[device_id] = 0
        
        if current_time - self.last_frame_time[device_id] > 0.1:
            self.frame_tasks[device_id] = set()
            self.last_frame_time[device_id] = current_time
        
        if task_name in self.frame_tasks[device_id]:
            return False
        
        last_time = self.last_execution[device_id].get(task_name, 0)
        # Task's own cooldown takes priority over global settings
        cooldown = default_cooldown if default_cooldown != 2.0 else self.cooldowns.get(task_name, default_cooldown)
        
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
            
            x, y, w, h = roi
            roi_img = screenshot[y:y+h, x:x+w]
            
            if roi_img.size == 0:
                continue
            
            result = cv2.matchTemplate(roi_img.astype(np.uint8), 
                                     template.astype(np.uint8), 
                                     cv2.TM_CCOEFF_NORMED)
            
            locations = np.where(result >= confidence)
            
            if len(locations[0]) == 0:
                continue
            
            matches = []
            template_h, template_w = template.shape[:2]
            
            for pt_y, pt_x in zip(locations[0], locations[1]):
                center_x = x + pt_x + template_w // 2
                center_y = y + pt_y + template_h // 2
                
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
            if settings.SPAM_LOGS:
                print(f"Error matching template {template_path}: {e}")
            continue
    
    return all_matches

async def batch_check_pixels_enhanced(device_id: str, tasks: List[dict], 
                                     screenshot: Optional[np.ndarray] = None) -> List[dict]:
    """Enhanced batch checking with proper task filtering"""
    if screenshot is not None:
        img_gpu = screenshot
    else:
        img_gpu = await screenshot_manager.get_screenshot(device_id)
    
    if img_gpu is None:
        return []
    
    # Filter tasks BEFORE processing them
    filtered_tasks = []
    for task in tasks:
        # Apply StopSupport and ConditionalRun filtering here too
        from background_process import monitor
        if not monitor.process_monitor.should_skip_task(device_id, task):
            filtered_tasks.append(task)
        else:
            # Debug logging for skipped Yukio tasks
            if "Yukio" in task.get("task_name", ""):
                print(f"[{device_id}] Pre-filtered out: {task.get('task_name')}")
    
    # Now process only the filtered tasks
    pixel_tasks = []
    template_tasks = []
    ocr_tasks = []
    shared_detection_tasks = []
    
    for task in filtered_tasks:  # Use filtered_tasks instead of tasks
        task_type = task.get("type", "pixel")
        
        if task_type == "pixel":
            pixel_tasks.append(task)
        elif task_type == "ocr":
            ocr_tasks.append(task)
        elif task_type == "template":
            if task.get("shared_detection", False):
                shared_detection_tasks.append(task)
            else:
                template_tasks.append(task)
    
    matched_tasks = []
    
    # Process pixel tasks
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
            task_cooldown = task.get("cooldown", 2.0)
            if task_tracker.can_execute_task(device_id, task["task_name"], task_cooldown):
                # Check for swipe functionality in pixel tasks
                swipe_command = task.get("swipe_command")
                min_matches_for_swipe = task.get("min_matches_for_swipe")
                multi_click = task.get("multi_click")
                
                # Check for swipe_count functionality (new feature)
                swipe_count = task.get("swipe_count")
                if swipe_command and swipe_count:
                    print(f"[SWIPE] {task['task_name']}: Executing swipe command {swipe_count} times")
                    print(f"[SWIPE] Command: {swipe_command}")
                    for i in range(swipe_count):
                        await run_adb_command(swipe_command, device_id)
                        if i < swipe_count - 1:  # Don't sleep after the last swipe
                            await asyncio.sleep(2.0)  # 2 second delay between swipes
                    task_copy = task.copy()
                    task_copy["task_name"] = f"{task['task_name']} [Swipe {swipe_count}x executed]"
                    matched_tasks.append(task_copy)
                    task_tracker.record_execution(device_id, task["task_name"])
                elif swipe_command and (multi_click or min_matches_for_swipe):
                    # For min_matches_for_swipe, we assume all pixels matched = 1 match
                    if min_matches_for_swipe and min_matches_for_swipe <= 1:
                        print(f"[SWIPE] {task['task_name']}: Pixel match meets swipe threshold ({min_matches_for_swipe})")
                        print(f"[SWIPE] Command: {swipe_command}")
                        await run_adb_command(swipe_command, device_id)
                        task_copy = task.copy()
                        task_copy["task_name"] = f"{task['task_name']} [Swipe executed]"
                        matched_tasks.append(task_copy)
                        task_tracker.record_execution(device_id, task["task_name"])
                    elif multi_click:
                        print(f"[SWIPE] {task['task_name']}: Executing swipe command")
                        print(f"[SWIPE] Command: {swipe_command}")
                        await run_adb_command(swipe_command, device_id)
                        task_copy = task.copy()
                        task_copy["task_name"] = f"{task['task_name']} [Swipe executed]"
                        matched_tasks.append(task_copy)
                        task_tracker.record_execution(device_id, task["task_name"])
                    else:
                        # min_matches_for_swipe > 1, but we only have 1 pixel match
                        matched_tasks.append(task)
                        if task.get("click_location_str") == "0,0":
                            task_tracker.record_execution(device_id, task["task_name"])
                else:
                    matched_tasks.append(task)
                    # IMPORTANT: Record execution immediately for detection-only tasks
                    if task.get("click_location_str") == "0,0":
                        task_tracker.record_execution(device_id, task["task_name"])
    
    # Process Pixel-OneOrMoreMatched tasks
    pixel_one_or_more_tasks = [task for task in tasks if task.get("type") == "Pixel-OneOrMoreMatched"]
    
    for task in pixel_one_or_more_tasks:
        pixel_values = task.get("pixel-values", [])
        if len(pixel_values) < 4:  # Need at least 2 pairs (coord, color, coord, color)
            continue
            
        match_found = False
        
        # Check consecutive pairs: (coord1, color1, coord2, color2), (color1, coord2, color2, coord3), etc.
        for i in range(0, len(pixel_values) - 3, 2):
            try:
                # Get first pair
                coords1_str = pixel_values[i]
                color1 = pixel_values[i + 1]
                
                # Get second pair  
                coords2_str = pixel_values[i + 2]
                color2 = pixel_values[i + 3]
                
                # Parse coordinates
                x1, y1 = map(int, coords1_str.split(','))
                x2, y2 = map(int, coords2_str.split(','))
                
                # Convert colors to RGB
                expected_rgb1 = hex_to_rgb(color1)
                expected_rgb2 = hex_to_rgb(color2)
                expected_rgb1_gpu = np.array(expected_rgb1)
                expected_rgb2_gpu = np.array(expected_rgb2)
                
                # Check if both pixels are within bounds and match
                if (0 <= y1 < img_gpu.shape[0] and 0 <= x1 < img_gpu.shape[1] and
                    0 <= y2 < img_gpu.shape[0] and 0 <= x2 < img_gpu.shape[1]):
                    
                    pixel_color1 = img_gpu[y1, x1]
                    pixel_color2 = img_gpu[y2, x2]
                    
                    if (np.array_equal(pixel_color1, expected_rgb1_gpu) and 
                        np.array_equal(pixel_color2, expected_rgb2_gpu)):
                        match_found = True
                        break
                        
            except (ValueError, IndexError):
                continue
        
        if match_found:
            task_cooldown = task.get("cooldown", 2.0)
            if task_tracker.can_execute_task(device_id, task["task_name"], task_cooldown):
                matched_tasks.append(task)
    
    # Process OCR tasks
    for task in ocr_tasks:
        ocr_text = task.get("ocr_text", "")
        if not ocr_text:
            continue
        
        # Parse search texts (comma-separated)
        search_texts = [text.strip().lower() for text in ocr_text.split(",")]
        
        roi = task.get("roi", [0, 0, img_gpu.shape[1], img_gpu.shape[0]])
        
        # Check if we can execute this task
        task_cooldown = task.get("cooldown", 2.0)
        if not task_tracker.can_execute_task(device_id, task["task_name"], task_cooldown):
            continue
        
        # Find text in region
        result = await ocr_manager.find_text_in_region(img_gpu, search_texts, roi)
        
        if result:
            matched_text, position = result
            task_copy = task.copy()
            
            # Handle position setting
            if task.get("use_match_position", False):
                # Only for single word/number searches (no comma)
                if "," not in ocr_text:
                    task_copy["click_location_str"] = f"{position[0]},{position[1]}"
                    task_copy["task_name"] = f"{task['task_name']} [OCR: '{matched_text}' at {position}]"
                else:
                    task_copy["task_name"] = f"{task['task_name']} [OCR: '{matched_text}' found]"
            else:
                task_copy["task_name"] = f"{task['task_name']} [OCR: '{matched_text}']"
            
            matched_tasks.append(task_copy)
            task_tracker.record_execution(device_id, task["task_name"])
    
    # Process shared detection templates
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
        
        all_matches = await find_all_templates_smart(img_gpu, templates_to_check)
        
        for template_path, positions in all_matches.items():
            task = task_map[template_path]
            task_name = task["task_name"]
            
            task_cooldown = task.get("cooldown", 2.0)
            if not task_tracker.can_execute_task(device_id, task_name, task_cooldown):
                if "Swipe All Tasks" in task_name:
                    print(f"[DEBUG] {task_name}: BLOCKED by cooldown ({task_cooldown}s)")
                continue
            
            if task.get("multi_click", False) or "UnClear" in task_name:
                if settings.SPAM_LOGS:
                    print(f"[MULTI-DETECT] {task_name}: Found {len(positions)} matches")
                
                # Check for swipe condition
                min_matches_for_swipe = task.get("min_matches_for_swipe")
                swipe_command = task.get("swipe_command")
                
                # Check for swipe_count functionality (new feature)
                swipe_count = task.get("swipe_count")
                if swipe_command and swipe_count:
                    print(f"[SWIPE] {task_name}: Executing swipe command {swipe_count} times")
                    print(f"[SWIPE] Command: {swipe_command}")
                    for i in range(swipe_count):
                        await run_adb_command(swipe_command, device_id)
                        if i < swipe_count - 1:  # Don't sleep after the last swipe
                            await asyncio.sleep(2.0)  # 2 second delay between swipes
                    task_copy = task.copy()
                    task_copy["task_name"] = f"{task_name} [Swipe {swipe_count}x executed]"
                    matched_tasks.append(task_copy)
                elif min_matches_for_swipe and swipe_command and len(positions) >= min_matches_for_swipe:
                    print(f"[SWIPE] {task_name}: {len(positions)} matches >= {min_matches_for_swipe}, executing swipe")
                    print(f"[SWIPE] Command: {swipe_command}")
                    await run_adb_command(swipe_command, device_id)
                    task_copy = task.copy()
                    task_copy["task_name"] = f"{task_name} [Swipe: {len(positions)} matches]"
                    matched_tasks.append(task_copy)
                else:
                    # Regular multi-click behavior
                    for i, (x, y) in enumerate(positions):
                        await execute_tap(device_id, f"{x},{y}")
                        await asyncio.sleep(0.05)
                    
                    task_copy = task.copy()
                    task_copy["task_name"] = f"{task_name} [Multi: {len(positions)} clicks]"
                    matched_tasks.append(task_copy)
                
                task_tracker.record_execution(device_id, task_name)
            else:
                # Check if this is a detection-only task with swipe functionality
                min_matches_for_swipe = task.get("min_matches_for_swipe")
                swipe_command = task.get("swipe_command")
                
                # Check for swipe_count functionality (new feature)
                swipe_count = task.get("swipe_count")
                if swipe_command and swipe_count:
                    print(f"[SWIPE] {task_name}: Executing swipe command {swipe_count} times")
                    print(f"[SWIPE] Command: {swipe_command}")
                    for i in range(swipe_count):
                        await run_adb_command(swipe_command, device_id)
                        if i < swipe_count - 1:  # Don't sleep after the last swipe
                            await asyncio.sleep(2.0)  # 2 second delay between swipes
                    task_copy = task.copy()
                    task_copy["task_name"] = f"{task_name} [Swipe {swipe_count}x executed]"
                    matched_tasks.append(task_copy)
                    task_tracker.record_execution(device_id, task_name)
                elif min_matches_for_swipe and swipe_command:
                    # Detection-only mode - check if swipe threshold is met
                    if len(positions) >= min_matches_for_swipe:
                        print(f"[SWIPE] {task_name}: {len(positions)} matches >= {min_matches_for_swipe}, executing swipe")
                        print(f"[SWIPE] Command: {swipe_command}")
                        await run_adb_command(swipe_command, device_id)
                        task_copy = task.copy()
                        task_copy["task_name"] = f"{task_name} [Swipe: {len(positions)} matches]"
                        matched_tasks.append(task_copy)
                    # If threshold not met, do nothing (detection-only)
                    task_tracker.record_execution(device_id, task_name)
                elif positions:
                    # Regular template matching behavior
                    x, y = positions[0]
                    task_copy = task.copy()
                    task_copy["click_location_str"] = f"{x},{y}"
                    task_copy["use_match_position"] = True
                    matched_tasks.append(task_copy)
                    task_tracker.record_execution(device_id, task_name)
    
    # Process regular template tasks
    for task in template_tasks:
        task_name = task["task_name"]
        
        task_cooldown = task.get("cooldown", 2.0)
        if not task_tracker.can_execute_task(device_id, task_name, task_cooldown):
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
                
                # Check for delayed click functionality
                delayed_click_location = task.get("delayed_click_location")
                delayed_click_delay = task.get("delayed_click_delay", 2.0)
                
                if delayed_click_location:
                    task_copy["delayed_click_location"] = delayed_click_location
                    task_copy["delayed_click_delay"] = delayed_click_delay
                
                # Check for swipe_count functionality (new feature for templates)
                swipe_count = task.get("swipe_count")
                swipe_command = task.get("swipe_command")
                
                if swipe_command and swipe_count:
                    print(f"[TEMPLATE SWIPE] {task_name}: Executing swipe command {swipe_count} times")
                    print(f"[TEMPLATE SWIPE] Command: {swipe_command}")
                    for i in range(swipe_count):
                        await run_adb_command(swipe_command, device_id)
                        if i < swipe_count - 1:  # Don't sleep after the last swipe
                            await asyncio.sleep(2.0)  # 2 second delay between swipes
                    task_copy["task_name"] = f"{task_name} [Template Swipe {swipe_count}x executed]"
                
                matched_tasks.append(task_copy)
                task_tracker.record_execution(device_id, task_name)
                match_found = True
                break
        
        if match_found:
            break
    
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

async def execute_swipe(device_id: str, x1: int, y1: int, x2: int, y2: int, duration: int):
    """Execute swipe command asynchronously"""
    await run_adb_command(f"shell input swipe {x1} {y1} {x2} {y2} {duration}", device_id)

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
        if settings.SPAM_LOGS:
            print(f"Template matching error: {e}")
        return None

# Configure default cooldowns
task_tracker.set_task_cooldown("Click [Skip]", 3.0)
task_tracker.set_task_cooldown("Connection Error - Retry", 5.0)
task_tracker.set_task_cooldown("Click [OK]", 2.0)

# Export the enhanced batch check function
batch_check_pixels = batch_check_pixels_enhanced