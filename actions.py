# actions.py - Optimized Version with Screenrecord Streaming
import asyncio
import subprocess
import io
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import os

import numpy as np
from PIL import Image
import cv2
from screenrecord_manager import get_screenrecord_manager, cleanup_all_screenrecord

# --- Screenshot Cache ---
@dataclass
class ScreenshotCache:
    """Caches screenshots to avoid redundant captures"""
    image: np.ndarray
    timestamp: float
    
class ScreenshotManager:
    def __init__(self, cache_duration: float = 0.1):  # Reduced cache duration for streaming
        self.cache: Dict[str, ScreenshotCache] = {}
        self.cache_duration = cache_duration
        self.locks: Dict[str, asyncio.Lock] = {}
        self.streaming_enabled = False  # Disable streaming - use ADB fallback only
    
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
            
            # Use ADB screencap directly (streaming disabled on Linux without FFmpeg)
            img = await self._capture_screenshot_adb(device_id)
            
            if img is not None:
                self.cache[device_id] = ScreenshotCache(img, current_time)
            return img
    
    async def _capture_screenshot_streaming(self, device_id: str) -> Optional[np.ndarray]:
        """Capture screenshot using screenrecord streaming (high performance)"""
        try:
            manager = await get_screenrecord_manager(device_id)
            if manager:
                return await manager.get_screenshot()
        except Exception as e:
            print(f"Screenrecord streaming failed for {device_id}: {e}")
            self.streaming_enabled = False  # Disable for this session
        return None
    
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
            
            # Process image on GPU
            pil_image = Image.open(io.BytesIO(stdout)).convert('RGB')
            return np.asarray(pil_image)
            
        except Exception as e:
            print(f"ADB screenshot failed for {device_id}: {e}")
            return None

# Global screenshot manager
screenshot_manager = ScreenshotManager()

# --- Template Matching Cache ---
class TemplateCache:
    """Cache for template images to avoid repeated loading"""
    def __init__(self):
        self.templates: Dict[str, np.ndarray] = {}
        self.cache_size_limit = 50  # Limit cache size to prevent memory issues
    
    def get_template(self, template_path: str) -> Optional[np.ndarray]:
        """Load and cache template image"""
        if template_path in self.templates:
            return self.templates[template_path]
        
        if not os.path.exists(template_path):
            print(f"Template not found: {template_path}")
            return None
        
        try:
            # Load template with OpenCV for consistency
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                return None
            
            # Convert BGR to RGB to match screenshot format
            template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
            
            # Cache management - remove oldest if limit reached
            if len(self.templates) >= self.cache_size_limit:
                # Remove first (oldest) entry
                self.templates.pop(next(iter(self.templates)))
            
            self.templates[template_path] = template
            return template
        except Exception as e:
            print(f"Error loading template {template_path}: {e}")
            return None

# Global template cache
template_cache = TemplateCache()

# --- Optimized Template Matching Functions ---
async def find_template_in_region(screenshot: np.ndarray, template_path: str, 
                                 roi: Tuple[int, int, int, int], 
                                 confidence: float = 0.9) -> Optional[Tuple[int, int]]:
    """
    Find template in a specific region of the screenshot.
    ROI format: (x, y, width, height)
    Returns: (x, y) of the best match center point, or None if not found
    """
    try:
        # Get cached template
        template = template_cache.get_template(template_path)
        if template is None:
            return None
        
        # Extract ROI from screenshot
        x, y, w, h = roi
        roi_img = screenshot[y:y+h, x:x+w]
        
        # Check if ROI is valid
        if roi_img.size == 0:
            return None
        
        # Use optimized template matching method
        # TM_CCOEFF_NORMED is fast and works well for most cases
        result = cv2.matchTemplate(roi_img.astype(np.uint8), 
                                  template.astype(np.uint8), 
                                  cv2.TM_CCOEFF_NORMED)
        
        # Find best match
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            # Calculate center point of match
            template_h, template_w = template.shape[:2]
            center_x = x + max_loc[0] + template_w // 2
            center_y = y + max_loc[1] + template_h // 2
            return (center_x, center_y)
        
        return None
        
    except Exception as e:
        print(f"Template matching error: {e}")
        return None

# --- Optimized Core Functions ---

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
        stderr=asyncio.subprocess.PIPE # MODIFIED: Use PIPE for better cleanup
    )
    
    stdout, stderr = await process.communicate()
    return stdout

async def batch_check_pixels(device_id: str, tasks: List[dict], screenshot: Optional[np.ndarray] = None) -> List[dict]:
    """Check multiple pixel or template conditions on a single screenshot"""
    if screenshot is not None:
        img_gpu = screenshot
    else:
        img_gpu = await screenshot_manager.get_screenshot(device_id)
    
    if img_gpu is None:
        return []
    
    matched_tasks = []
    
    for task in tasks:
        # Check task type (default to pixel for backward compatibility)
        task_type = task.get("type", "pixel")
        
        if task_type == "pixel":
            # Original pixel matching logic
            search_array = task["search_array"]
            all_match = True
            
            for i in range(0, len(search_array), 2):
                coords_str, hex_color = search_array[i], search_array[i+1]
                x, y = map(int, coords_str.split(','))
                
                expected_rgb = hex_to_rgb(hex_color)
                expected_rgb_gpu = np.array(expected_rgb)
                
                # Bounds checking
                if 0 <= y < img_gpu.shape[0] and 0 <= x < img_gpu.shape[1]:
                    pixel_color_gpu = img_gpu[y, x]
                    if not np.array_equal(pixel_color_gpu, expected_rgb_gpu):
                        all_match = False
                        break
                else:
                    all_match = False
                    break
            
            if all_match:
                matched_tasks.append(task)
                
        elif task_type == "template":
            # Template matching logic
            template_path = task.get("template_path")
            roi = task.get("roi")  # (x, y, width, height)
            confidence = task.get("confidence", 0.9)
            
            if template_path and roi:
                match_pos = await find_template_in_region(img_gpu, template_path, roi, confidence)
                if match_pos:
                    # Update click location to the matched position if needed
                    if task.get("use_match_position", False):
                        task["click_location_str"] = f"{match_pos[0]},{match_pos[1]}"
                    matched_tasks.append(task)
    
    return matched_tasks

async def execute_tap(device_id: str, location_str: str):
    """Execute tap command asynchronously"""
    coords = location_str.replace(',', ' ')
    await run_adb_command(f"shell input tap {coords}", device_id)

async def search_pixels_and_click(device_id: str, click_location_str: str, 
                                search_array: List[str], isLogical: bool = False) -> bool:
    """Backward compatible function using the optimized screenshot manager"""
    img_gpu = await screenshot_manager.get_screenshot(device_id)
    if img_gpu is None:
        return False

    all_match = True
    for i in range(0, len(search_array), 2):
        coords_str, hex_color = search_array[i], search_array[i+1]
        x, y = map(int, coords_str.split(','))
        
        expected_rgb_gpu = np.array(hex_to_rgb(hex_color))
        
        if 0 <= y < img_gpu.shape[0] and 0 <= x < img_gpu.shape[1]:
            pixel_color_gpu = img_gpu[y, x]
            if not np.array_equal(pixel_color_gpu, expected_rgb_gpu):
                all_match = False
                break
        else:
            all_match = False
            break
            
    if all_match:
        print(f"[{device_id}] Match found. Clicking {click_location_str}.")
        await execute_tap(device_id, click_location_str)
        
        if isLogical:
            print(f"[{device_id}] Logical trigger activated!")
            return True
            
    return False