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
    """Enhanced OCR Manager optimized for game UI number extraction"""
    
    def __init__(self):
        self.ocr_cache: Dict[str, Dict] = {}
        self.cache_duration = 0.5
        
        # Initialize multiple EasyOCR readers if available
        if EASYOCR_AVAILABLE:
            self.ocr_reader = easyocr.Reader(['en'], gpu=True)
            # Additional reader for pure numbers
            try:
                self.ocr_reader_digits = easyocr.Reader(['en'], gpu=True, recog_network='digit')
            except:
                self.ocr_reader_digits = self.ocr_reader
    
    async def extract_numbers_enhanced(self, screenshot: np.ndarray, 
                                      roi: Tuple[int, int, int, int],
                                      is_id: bool = False) -> str:
        """
        Enhanced number extraction with multiple preprocessing passes.
        is_id: True if extracting IDs (expects spaces), False for regular numbers (commas)
        """
        x, y, w, h = roi
        roi_img = screenshot[y:y+h, x:x+w]
        
        if roi_img.size == 0:
            return ""
        
        # Try multiple preprocessing strategies
        results = []
        
        # Strategy 1: Upscale + Sharp contrast
        preprocessed_1 = self._preprocess_for_numbers(roi_img, scale=3, invert=False)
        result_1 = await self._ocr_pass(preprocessed_1, digits_only=not is_id)
        if result_1:
            results.append((result_1, self._calculate_confidence(result_1, is_id)))
        
        # Strategy 2: Inverted colors
        preprocessed_2 = self._preprocess_for_numbers(roi_img, scale=3, invert=True)
        result_2 = await self._ocr_pass(preprocessed_2, digits_only=not is_id)
        if result_2:
            results.append((result_2, self._calculate_confidence(result_2, is_id)))
        
        # Strategy 3: Adaptive threshold
        preprocessed_3 = self._preprocess_adaptive(roi_img)
        result_3 = await self._ocr_pass(preprocessed_3, digits_only=not is_id)
        if result_3:
            results.append((result_3, self._calculate_confidence(result_3, is_id)))
        
        # Strategy 4: Color isolation (for colored text)
        preprocessed_4 = self._preprocess_color_isolation(roi_img)
        result_4 = await self._ocr_pass(preprocessed_4, digits_only=not is_id)
        if result_4:
            results.append((result_4, self._calculate_confidence(result_4, is_id)))
        
        # Strategy 5: Enhanced comma detection (for numbers only)
        if not is_id:
            preprocessed_5 = self._preprocess_for_commas(roi_img)
            result_5 = await self._ocr_pass(preprocessed_5, digits_only=True)
            if result_5:
                results.append((result_5, self._calculate_confidence(result_5, is_id)))
        
        # Select best result based on confidence
        if results:
            best_result = max(results, key=lambda x: x[1])
            return self._post_process_numbers(best_result[0], is_id)
        
        return ""
    
    def _preprocess_for_numbers(self, img: np.ndarray, scale: int = 2, invert: bool = False) -> np.ndarray:
        """Advanced preprocessing optimized for game UI numbers"""
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img.copy()
        
        # Upscale for better OCR accuracy
        if scale > 1:
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Denoise
        gray = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Enhance contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        gray = cv2.filter2D(gray, -1, kernel)
        
        # Binary threshold
        if invert:
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        else:
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up
        kernel = np.ones((2,2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        return thresh
    
    def _preprocess_for_commas(self, img: np.ndarray) -> np.ndarray:
        """Special preprocessing to enhance comma detection in numbers"""
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img.copy()
        
        # Heavy upscaling for comma detection
        gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        
        # Gaussian blur to merge nearby elements
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Enhance contrast specifically for punctuation
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4,4))
        gray = clahe.apply(gray)
        
        # Custom threshold that preserves small details like commas
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological closing to connect broken characters
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return thresh
    
    def _preprocess_adaptive(self, img: np.ndarray) -> np.ndarray:
        """Adaptive threshold preprocessing"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img.copy()
        
        # Upscale
        gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        
        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 11, 2)
        
        return thresh
    
    def _preprocess_color_isolation(self, img: np.ndarray) -> np.ndarray:
        """Isolate specific color ranges (useful for colored game text)"""
        if len(img.shape) != 3:
            return img
        
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        
        # Try to isolate bright/light colors (common for game UI)
        lower_bound = np.array([0, 0, 100])
        upper_bound = np.array([180, 100, 255])
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        # Upscale
        mask = cv2.resize(mask, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        
        return mask
    
    async def _ocr_pass(self, img: np.ndarray, digits_only: bool = False) -> str:
        """Perform OCR with specified configuration"""
        detected_text = ""
        
        try:
            if EASYOCR_AVAILABLE:
                # Use EasyOCR
                if digits_only and hasattr(self, 'ocr_reader_digits'):
                    results = self.ocr_reader_digits.readtext(img, 
                                                             allowlist='0123456789,. ',
                                                             detail=1)
                else:
                    allowlist = '0123456789,. :ID' if not digits_only else '0123456789,. '
                    results = self.ocr_reader.readtext(img, 
                                                      allowlist=allowlist,
                                                      detail=1)
                
                # Combine results
                texts = []
                for (bbox, text, confidence) in results:
                    if confidence > 0.3:  # Lower threshold for multiple passes
                        texts.append(text)
                detected_text = ' '.join(texts)
                
            elif TESSERACT_AVAILABLE:
                # Tesseract with digit-specific config
                if digits_only:
                    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789, '
                else:
                    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789,:ID '
                
                detected_text = pytesseract.image_to_string(img, config=custom_config)
                
        except Exception as e:
            print(f"OCR pass error: {e}")
        
        return detected_text.strip()
    
    def _calculate_confidence(self, text: str, is_id: bool) -> float:
        """Calculate confidence score for extracted text"""
        if not text:
            return 0.0
        
        confidence = 1.0
        
        # Check for expected format
        if is_id:
            # ID format: should have "ID:" and numbers with spaces
            if "ID" not in text and "id" not in text:
                confidence *= 0.5
            # Should have spaces between number groups
            if ' ' not in text:
                confidence *= 0.7
        else:
            # Number format: should have digits and possibly commas
            digit_ratio = sum(1 for c in text if c.isdigit()) / len(text)
            confidence *= digit_ratio
        
        # Penalize for unexpected characters (allow dashes for ID format)
        allowed_chars = '0123456789,. :ID-' if is_id else '0123456789,. :ID'
        unexpected_chars = sum(1 for c in text if c not in allowed_chars)
        confidence *= (1.0 - unexpected_chars * 0.1)
        
        return max(0, min(1, confidence))
    
    def _post_process_numbers(self, text: str, is_id: bool) -> str:
        """Clean up and format extracted numbers"""
        if not text:
            return ""
        
        # Remove common OCR artifacts
        text = text.replace('|', '1')
        text = text.replace('l', '1')
        text = text.replace('O', '0')
        text = text.replace('o', '0')
        text = text.replace('S', '5')
        text = text.replace('Z', '2')
        text = text.replace('B', '8')
        text = text.replace('G', '6')
        text = text.replace('§', '5')
        text = text.replace('¢', 'c')
        
        # Additional comma-specific fixes for numbers like "21,124"
        if not is_id:
            # Fix cases where comma is read as other characters
            text = text.replace('.', ',')  # period misread as comma
            text = text.replace(';', ',')  # semicolon misread as comma
            text = text.replace(':', ',')  # colon misread as comma
            text = text.replace('`', ',')  # backtick misread as comma
            text = text.replace("'", ',')  # apostrophe misread as comma
        
        if is_id:
            # Clean ID format - handle both "ID: XX XXX XXX" and "ID:123-12-3123-123"
            text = text.upper()
            
            # Look for ID pattern and extract everything after "ID:"
            import re
            id_match = re.search(r'ID[:\s]+([0-9\-\s]+)', text)
            if id_match:
                id_part = id_match.group(1).strip()
                # Keep original formatting with dashes if present
                if '-' in id_part:
                    # Format like "ID:123-12-3123-123"
                    return f"ID:{id_part}"
                else:
                    # Format like "ID: 88 534 886" 
                    numbers = ''.join(filter(lambda x: x.isdigit(), id_part))
                    if len(numbers) >= 6:
                        # Try to format nicely
                        if len(numbers) == 8:  # Format: XX XXX XXX
                            formatted = f"{numbers[:2]} {numbers[2:5]} {numbers[5:]}"
                        elif len(numbers) == 9:  # Format: XXX XXX XXX
                            formatted = f"{numbers[:3]} {numbers[3:6]} {numbers[6:]}"
                        else:
                            formatted = numbers
                        return f"ID: {formatted}"
                    else:
                        return f"ID: {id_part}"
            
            # Fallback: look for any ID-like pattern
            id_fallback = re.search(r'(ID[:\s]*[0-9\-\s]+)', text)
            if id_fallback:
                return id_fallback.group(1).strip()
                
            return text.strip()
        else:
            # Clean number format (with commas)
            # Extract only digits and commas
            numbers = ''.join(filter(lambda x: x.isdigit() or x == ',', text))
            
            # Smart comma detection and correction
            numbers = self._fix_comma_misreads(numbers)
            
            # Fix comma placement if needed
            if ',' not in numbers and len(numbers) > 3:
                # Add commas for thousands
                reversed_num = numbers[::-1]
                formatted = ','.join([reversed_num[i:i+3] for i in range(0, len(reversed_num), 3)])
                numbers = formatted[::-1]
            
            return numbers
    
    def _fix_comma_misreads(self, numbers: str) -> str:
        """Fix common comma misreads in number strings"""
        if not numbers or ',' in numbers:
            # Already has commas or empty
            return numbers
        
        # Pattern detection for common misreads
        # Case 1: "211240" should be "21,124" (comma read as 0)
        # Look for patterns where a number ends with 0 in wrong place
        if len(numbers) == 6 and numbers.endswith('0'):
            # Try pattern: XX,XXX (like 21,124 → 211240)
            if numbers[2] == '0' and numbers[-1] == '0':
                # Remove the misread zero and add comma
                fixed = numbers[:2] + ',' + numbers[3:-1]
                return fixed
        
        # Case 2: "21124" should be "21,124" (comma completely missing)
        if len(numbers) == 5:
            # Standard thousands format: XX,XXX
            return numbers[:2] + ',' + numbers[2:]
        
        # Case 3: Other patterns based on typical number lengths
        if len(numbers) == 6 and not numbers.endswith('0'):
            # Could be XXX,XXX format
            return numbers[:3] + ',' + numbers[3:]
        elif len(numbers) == 7:
            # Could be X,XXX,XXX format
            return numbers[:1] + ',' + numbers[1:4] + ',' + numbers[4:]
        
        return numbers
    
    async def extract_text_from_region(self, screenshot: np.ndarray, 
                                      roi: Tuple[int, int, int, int],
                                      use_easyocr: bool = True) -> List[Tuple[str, Tuple[int, int]]]:
        """Enhanced version with number optimization"""
        x, y, w, h = roi
        roi_img = screenshot[y:y+h, x:x+w]
        
        if roi_img.size == 0:
            return []
        
        # Check if this looks like a number region
        is_number_region = self._is_likely_number_region(roi_img)
        
        if is_number_region:
            # Use enhanced number extraction
            extracted = await self.extract_numbers_enhanced(screenshot, roi, is_id=False)
            if extracted:
                center_x = x + w // 2
                center_y = y + h // 2
                return [(extracted, (center_x, center_y))]
        
        # Fall back to original implementation for text
        return await self._original_extract_text(screenshot, roi, use_easyocr)
    
    def _is_likely_number_region(self, img: np.ndarray) -> bool:
        """Heuristic to detect if region likely contains numbers"""
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
        
        # Check if text is likely present (high contrast areas)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        white_pixels = np.sum(binary == 255)
        total_pixels = binary.size
        
        # If 10-90% white pixels, likely contains text
        ratio = white_pixels / total_pixels
        return 0.1 < ratio < 0.9
    
    async def _original_extract_text(self, screenshot: np.ndarray, 
                                    roi: Tuple[int, int, int, int],
                                    use_easyocr: bool = True) -> List[Tuple[str, Tuple[int, int]]]:
        """Original extract_text_from_region implementation"""
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

    async def extract_orbs_ultra_robust(self, screenshot: np.ndarray, device_id: str) -> str:
        """
        Ultra-robust orb extraction with multiple strategies and validation.
        Guarantees correct format: XX,XXX (like 21,137)
        """
        # Define multiple ROI variations for better coverage (more conservative)
        roi_variations = [
            [725, 5, 53, 29],
            [722, 6, 57, 24],
            [724, 9, 57, 18],
            [726, 10, 51, 16],
        ]
        
        all_results = []
        start_time = time.time()
        max_extraction_time = 30.0  # 30 second timeout
        
        for roi_idx, roi in enumerate(roi_variations):
            # Check timeout
            if time.time() - start_time > max_extraction_time:
                print(f"[{device_id}] ⏰ Extraction timeout after {max_extraction_time}s, using current results")
                break
                
            x, y, w, h = roi
            roi_img = screenshot[y:y+h, x:x+w]
            
            if roi_img.size == 0:
                continue
            
            # Try 8 different preprocessing strategies per ROI
            strategies = [
                # Strategy 1: Standard with different scales
                lambda img: self._preprocess_orb_v1(img, scale=2),
                lambda img: self._preprocess_orb_v1(img, scale=3),
                lambda img: self._preprocess_orb_v1(img, scale=4),
                
                # Strategy 2: Inverted
                lambda img: self._preprocess_orb_v2(img, invert=True),
                lambda img: self._preprocess_orb_v2(img, invert=False),
                
                # Strategy 3: Enhanced comma detection
                lambda img: self._preprocess_orb_comma_enhanced(img),
                
                # Strategy 4: Morphological focus
                lambda img: self._preprocess_orb_morphological(img),
                
                # Strategy 5: Edge detection based
                lambda img: self._preprocess_orb_edge_based(img)
            ]
            
            for strat_idx, strategy in enumerate(strategies):
                try:
                    preprocessed = strategy(roi_img)
                    
                    # Try both EasyOCR and Tesseract
                    if EASYOCR_AVAILABLE:
                        # EasyOCR with strict whitelist
                        results = self.ocr_reader.readtext(preprocessed, 
                                                          allowlist='0123456789,',
                                                          detail=1)
                        for (bbox, text, confidence) in results:
                            if confidence > 0.3 and text:
                                cleaned = self._validate_orb_format(text, device_id)
                                if cleaned:
                                    all_results.append({
                                        'value': cleaned,
                                        'confidence': confidence,
                                        'method': f'easyocr_roi{roi_idx}_strat{strat_idx}'
                                    })
                                    
                                    # Early success detection - if we have a high-confidence reasonable result
                                    if confidence > 0.85 and len(all_results) >= 8 and self._is_reasonable_orb_value(cleaned):
                                        early_consensus = self._get_orb_consensus_ultra(all_results, device_id)
                                        if early_consensus != "0" and self._is_reasonable_orb_value(early_consensus):
                                            print(f"[{device_id}] 🎯 Early consensus found: {early_consensus}")
                                            return early_consensus
                    
                    if TESSERACT_AVAILABLE:
                        # Tesseract with multiple PSM modes
                        for psm in [7, 8, 11, 13]:
                            config = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789,'
                            text = pytesseract.image_to_string(preprocessed, config=config).strip()
                            if text:
                                cleaned = self._validate_orb_format(text, device_id)
                                if cleaned:
                                    all_results.append({
                                        'value': cleaned,
                                        'confidence': 0.5,  # Default confidence for Tesseract
                                        'method': f'tesseract_roi{roi_idx}_strat{strat_idx}_psm{psm}'
                                    })
                    
                except Exception:
                    continue
        
        # Intelligent consensus with validation
        return self._get_orb_consensus_ultra(all_results, device_id)

    def _preprocess_orb_v1(self, img: np.ndarray, scale: int = 3) -> np.ndarray:
        """Standard preprocessing with scaling"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img.copy()
        
        # Upscale
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Denoise
        gray = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # CLAHE for contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # Binary threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh

    def _preprocess_orb_v2(self, img: np.ndarray, invert: bool = False) -> np.ndarray:
        """Preprocessing with optional inversion"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img.copy()
        
        # Heavy upscaling
        gray = cv2.resize(gray, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)
        
        # Bilateral filter for edge preservation
        gray = cv2.bilateralFilter(gray, 11, 75, 75)
        
        if invert:
            gray = cv2.bitwise_not(gray)
        
        # Adaptive threshold
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 15, 3)
        
        return thresh

    def _preprocess_orb_comma_enhanced(self, img: np.ndarray) -> np.ndarray:
        """Special preprocessing to enhance comma detection"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img.copy()
        
        # Extreme upscaling for comma
        gray = cv2.resize(gray, None, fx=6, fy=6, interpolation=cv2.INTER_LANCZOS4)
        
        # Unsharp masking to enhance edges
        gaussian = cv2.GaussianBlur(gray, (0, 0), 2.0)
        gray = cv2.addWeighted(gray, 1.5, gaussian, -0.5, 0)
        
        # Morphological gradient to highlight edges
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        gradient = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, kernel)
        
        # Combine original with gradient
        gray = cv2.addWeighted(gray, 0.7, gradient, 0.3, 0)
        
        # Final threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh

    def _preprocess_orb_morphological(self, img: np.ndarray) -> np.ndarray:
        """Morphological operations focused preprocessing"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img.copy()
        
        # Moderate upscaling
        gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        
        # Top hat to extract light objects on dark background
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
        tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
        
        # Add back to original
        gray = cv2.add(gray, tophat)
        
        # Binary threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Clean up with morphology
        kernel_clean = np.ones((2, 2), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel_clean)
        
        return thresh

    def _preprocess_orb_edge_based(self, img: np.ndarray) -> np.ndarray:
        """Edge detection based preprocessing"""
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img.copy()
        
        # Upscale
        gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        
        # Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Dilate edges to connect broken parts
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
        
        return edges

    def _validate_orb_format(self, text: str, device_id: str) -> str:
        """
        Validate and fix orb format to match XX,XXX pattern.
        Returns None if format is invalid.
        """
        if not text:
            return None
        
        # Clean the text
        text = text.strip()
        
        # Remove any spaces
        text = text.replace(' ', '')
        
        # Common OCR fixes
        replacements = {
            '.': ',',
            ';': ',',
            ':': ',',
            '`': ',',
            "'": ',',
            'l': '1',
            'I': '1',
            'O': '0',
            'o': '0',
            'S': '5',
            's': '5',
            'Z': '2',
            'z': '2',
            'B': '8',
            'G': '6'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Check if it already has correct format (XX,XXX)
        if ',' in text:
            parts = text.split(',')
            if len(parts) == 2:
                before_comma = parts[0]
                after_comma = parts[1]
                
                # Validate format: 1-3 digits before comma, exactly 3 after
                if before_comma.isdigit() and after_comma.isdigit():
                    if 1 <= len(before_comma) <= 3 and len(after_comma) == 3:
                        return f"{before_comma},{after_comma}"
                    elif len(after_comma) > 3:
                        # Truncate extra digits
                        return f"{before_comma},{after_comma[:3]}"
        
        # Try to fix missing comma
        digits = ''.join(c for c in text if c.isdigit())
        
        # Be more restrictive - only allow reasonable orb counts
        if len(digits) == 5:  # XX,XXX format
            candidate = f"{digits[:2]},{digits[2:]}"
            if self._is_reasonable_orb_value(candidate):
                return candidate
        elif len(digits) == 4:  # X,XXX format  
            candidate = f"{digits[0]},{digits[1:]}"
            if self._is_reasonable_orb_value(candidate):
                return candidate
        elif len(digits) == 6:  # XXX,XXX format - be very careful
            candidate = f"{digits[:3]},{digits[3:]}"
            # Only allow if the first part is reasonable (under 100)
            if int(digits[:3]) <= 99 and self._is_reasonable_orb_value(candidate):
                return candidate
        
        return None

    def _is_reasonable_orb_value(self, orb_str: str) -> bool:
        """Check if orb value is within reasonable bounds"""
        try:
            if ',' not in orb_str:
                return False
            
            parts = orb_str.split(',')
            if len(parts) != 2:
                return False
                
            before_comma = int(parts[0])
            after_comma = int(parts[1])
            
            # Reasonable bounds for orb values
            # Before comma: 1-99 (not 200+ which is clearly wrong)
            # After comma: 000-999
            if not (1 <= before_comma <= 99):
                return False
            if not (0 <= after_comma <= 999):
                return False
            
            total_value = before_comma * 1000 + after_comma
            # Total orbs should be reasonable (1,000 to 99,999)
            if not (1000 <= total_value <= 99999):
                return False
                
            return True
        except:
            return False

    def _get_orb_consensus_ultra(self, all_results: list, device_id: str) -> str:
        """
        Ultra-robust consensus algorithm.
        """
        if not all_results:
            print(f"[{device_id}] No valid OCR results")
            return "0"
        
        # Count frequency of each value
        value_counts = {}
        for result in all_results:
            value = result['value']
            if value not in value_counts:
                value_counts[value] = {'count': 0, 'total_confidence': 0}
            value_counts[value]['count'] += 1
            value_counts[value]['total_confidence'] += result['confidence']
        
        # Score each unique value with improved logic
        scored_values = []
        for value, stats in value_counts.items():
            score = 0
            avg_confidence = stats['total_confidence'] / stats['count']
            
            # Strict reasonableness check first
            if not self._is_reasonable_orb_value(value):
                print(f"[{device_id}] ❌ Rejecting unreasonable value: {value}")
                continue
            
            # Confidence score (more important now)
            score += avg_confidence * 100
            
            # Frequency bonus (but less important)
            score += stats['count'] * 20
            
            # Format validation bonus
            if ',' in value:
                parts = value.split(',')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    if len(parts[1]) == 3:  # Exactly 3 digits after comma
                        score += 30
                    if 1 <= len(parts[0]) <= 2:  # 1-2 digits before comma (typical)
                        score += 40
                    elif len(parts[0]) == 3:  # 3 digits before comma (less common)
                        score += 20
            
            # Penalize values that seem too different from typical ranges
            try:
                numeric_value = int(value.replace(',', ''))
                # Typical orb range bonus
                if 5000 <= numeric_value <= 50000:  # Most common range
                    score += 25
                elif 1000 <= numeric_value <= 99999:  # Acceptable range
                    score += 10
            except:
                score -= 100
            
            scored_values.append({
                'value': value,
                'score': score,
                'count': stats['count'],
                'avg_confidence': stats['total_confidence'] / stats['count']
            })
        
        # Sort by score
        scored_values.sort(key=lambda x: x['score'], reverse=True)
        
        # Log results
        print(f"[{device_id}] OCR Consensus Analysis:")
        print(f"[{device_id}] Total attempts: {len(all_results)}")
        print(f"[{device_id}] Unique values: {len(scored_values)}")
        for sv in scored_values[:5]:  # Show top 5
            print(f"[{device_id}]   '{sv['value']}' - Score: {sv['score']:.1f}, Count: {sv['count']}, Avg Conf: {sv['avg_confidence']:.2f}")
        
        # Return the best scoring value
        if scored_values and scored_values[0]['score'] > 30:
            best = scored_values[0]['value']
            print(f"[{device_id}] ✅ Final orb value: {best}")
            return best
        
        print(f"[{device_id}] ⚠️ No reliable consensus, using fallback")
        return "0"

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
    ultra_robust_orb_tasks = []
    
    for task in filtered_tasks:  # Use filtered_tasks instead of tasks
        task_type = task.get("type", "pixel")
        
        if task_type == "pixel":
            pixel_tasks.append(task)
        elif task_type == "ocr":
            ocr_tasks.append(task)
        elif task_type == "ultra_robust_orb":
            ultra_robust_orb_tasks.append(task)
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
                    # Check for special screenshot saving functionality
                    if task.get("save_screenshot_with_username", False):
                        await save_screenshot_with_username(device_id, img_gpu)
                        task_copy = task.copy()
                        task_copy["task_name"] = f"{task['task_name']} [Screenshot saved with username]"
                        matched_tasks.append(task_copy)
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
    
    # Process ultra robust orb extraction tasks
    for task in ultra_robust_orb_tasks:
        task_cooldown = task.get("cooldown", 60.0)
        if not task_tracker.can_execute_task(device_id, task["task_name"], task_cooldown):
            continue
        
        print(f"[{device_id}] 🚀 Starting ultra-robust orb extraction...")
        
        # Apply pre-delay
        pre_delay = task.get("pre_delay", 0)
        if pre_delay > 0:
            print(f"[{device_id}] ⏳ Waiting {pre_delay}s for screen stabilization...")
            await asyncio.sleep(pre_delay)
        
        # Use the new ultra-robust extraction
        start_time = time.time()
        extracted_orb = await ocr_manager.extract_orbs_ultra_robust(img_gpu, device_id)
        extraction_time = time.time() - start_time
        print(f"[{device_id}] ⏱️ Extraction completed in {extraction_time:.2f}s")
        
        # Always record execution to prevent infinite retries
        task_tracker.record_execution(device_id, task["task_name"])
        
        if extracted_orb and extracted_orb != "0":
            # Validate one more time before saving
            if ',' in extracted_orb:
                parts = extracted_orb.split(',')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit() and len(parts[1]) == 3:
                    # Save to device state
                    from device_state_manager import device_state_manager
                    device_state_manager.update_state(device_id, "Orbs", extracted_orb)
                    
                    task_copy = task.copy()
                    task_copy["task_name"] = f"{task['task_name']} [✅ Orbs: {extracted_orb} saved]"
                    matched_tasks.append(task_copy)
                    print(f"[{device_id}] ✅ Orb extraction successful: {extracted_orb}")
                else:
                    print(f"[{device_id}] ⚠️ Invalid format after extraction: {extracted_orb}")
                    task_copy = task.copy()
                    task_copy["task_name"] = f"{task['task_name']} [❌ Invalid format: {extracted_orb}]"
                    matched_tasks.append(task_copy)
            else:
                print(f"[{device_id}] ⚠️ No comma in extracted value: {extracted_orb}")
                task_copy = task.copy()
                task_copy["task_name"] = f"{task['task_name']} [❌ No comma: {extracted_orb}]"
                matched_tasks.append(task_copy)
        else:
            print(f"[{device_id}] ❌ Orb extraction failed - no valid result")
            task_copy = task.copy()
            task_copy["task_name"] = f"{task['task_name']} [❌ No result]"
            matched_tasks.append(task_copy)
    
    # Process OCR tasks
    for task in ocr_tasks:
        roi = task.get("roi", [0, 0, img_gpu.shape[1], img_gpu.shape[0]])
        
        # Check if we can execute this task
        task_cooldown = task.get("cooldown", 2.0)
        if not task_tracker.can_execute_task(device_id, task["task_name"], task_cooldown):
            continue
        
        # Check if this is an enhanced number extraction task
        is_id = task.get("is_id")
        
        if is_id is not None:  # Support both True and False when explicitly set
            # Use enhanced number extraction for number/ID detection
            extracted_text = await ocr_manager.extract_numbers_enhanced(img_gpu, roi, is_id=is_id)
            
            # Always create task_copy for potential processing
            task_copy = task.copy()
            center_x = roi[0] + roi[2] // 2
            center_y = roi[1] + roi[3] // 2
            
            if extracted_text:
                
                # Store OCR result for orb consensus checking (for new multi-attempt system)
                if task.get("temp_orb_storage", False) or task.get("orb_consensus_check", False):
                    corrected_text = ocr_manager._fix_comma_misreads(extracted_text)
                    task_copy["ocr_result"] = corrected_text
                    task_copy["task_name"] = f"{task['task_name']} [OCR: '{extracted_text}' → '{corrected_text}']"
                    matched_tasks.append(task_copy)
                    task_tracker.record_execution(device_id, task["task_name"])
                # Store OCR result for account ID consensus checking
                elif task.get("temp_account_id_storage", False) or task.get("account_id_consensus_check", False):
                    task_copy["ocr_result"] = extracted_text  # Keep original for ID (no comma fixing needed)
                    task_copy["task_name"] = f"{task['task_name']} [OCR: '{extracted_text}']"
                    matched_tasks.append(task_copy)
                    task_tracker.record_execution(device_id, task["task_name"])
                # Special handling for orb value extraction (legacy single-attempt)
                elif task.get("extract_orb_value", False):
                    try:
                        # Apply smart pattern correction first
                        corrected_text = ocr_manager._fix_comma_misreads(extracted_text)
                        # Only accept values that contain comma (properly formatted currency)
                        if corrected_text and corrected_text.strip() and ',' in corrected_text:
                            # Import here to avoid circular import
                            from device_state_manager import device_state_manager
                            device_state_manager.update_state(device_id, "Orbs", corrected_text)
                            task_copy["task_name"] = f"{task['task_name']} [✅ Orbs: {extracted_text} → {corrected_text} saved to JSON]"
                            matched_tasks.append(task_copy)
                            task_tracker.record_execution(device_id, task["task_name"])
                        else:
                            # Reject values without comma - keep searching
                            if task.get("search_for_orb_pattern", True):  # Default to keep searching
                                display_text = corrected_text if corrected_text else extracted_text
                                task_copy["task_name"] = f"{task['task_name']} [🔍 Searching for comma-formatted orbs... ('{display_text}' rejected)]"
                                matched_tasks.append(task_copy)
                                # Don't record execution to keep searching
                                continue
                            else:
                                task_copy["task_name"] = f"{task['task_name']} [No valid orbs detected: '{corrected_text}']"
                                matched_tasks.append(task_copy)
                                task_tracker.record_execution(device_id, task["task_name"])
                    except Exception as e:
                        task_copy["task_name"] = f"{task['task_name']} [Error extracting orbs: {e}]"
                        matched_tasks.append(task_copy)
                        task_tracker.record_execution(device_id, task["task_name"])
                # Special handling for account ID value extraction
                elif task.get("extract_account_id_value", False):
                    try:
                        # Check if this text contains an ID pattern
                        if extracted_text and "ID" in extracted_text.upper():
                            # Import here to avoid circular import
                            from device_state_manager import device_state_manager
                            device_state_manager.update_state(device_id, "AccountID", extracted_text.strip())
                            task_copy["task_name"] = f"{task['task_name']} [✅ Account ID Found: {extracted_text} → Saved to JSON]"
                            # Mark as successful so NextTaskSet_Tasks can trigger
                            task_copy["id_extraction_successful"] = True
                            matched_tasks.append(task_copy)
                            task_tracker.record_execution(device_id, task["task_name"])
                        else:
                            # Keep searching - don't record execution to allow continuous searching
                            if task.get("search_for_id_pattern", False):
                                display_text = extracted_text[:20] if extracted_text else "nothing"
                                task_copy["task_name"] = f"{task['task_name']} [🔍 Searching for ID pattern... ('{display_text}' found)]"
                                matched_tasks.append(task_copy)
                                # Don't record execution to keep searching
                                continue
                            else:
                                task_copy["task_name"] = f"{task['task_name']} [No account ID detected: '{extracted_text}']"
                                matched_tasks.append(task_copy)
                                task_tracker.record_execution(device_id, task["task_name"])
                    except Exception as e:
                        task_copy["task_name"] = f"{task['task_name']} [Error extracting account ID: {e}]"
                        matched_tasks.append(task_copy)
                        task_tracker.record_execution(device_id, task["task_name"])
                else:
                    # Handle position setting for enhanced extraction
                    if task.get("use_match_position", False):
                        task_copy["click_location_str"] = f"{center_x},{center_y}"
                        task_copy["task_name"] = f"{task['task_name']} [Enhanced OCR: '{extracted_text}' at ({center_x},{center_y})]"
                    else:
                        task_copy["task_name"] = f"{task['task_name']} [Enhanced OCR: '{extracted_text}']"
                
                matched_tasks.append(task_copy)
                task_tracker.record_execution(device_id, task["task_name"])
            else:
                # Handle case when no text is extracted (empty OCR result)
                if task.get("temp_orb_storage", False) or task.get("orb_consensus_check", False):
                    # Store empty result for orb consensus checking
                    task_copy["ocr_result"] = ""
                    task_copy["task_name"] = f"{task['task_name']} [OCR: no text detected]"
                    matched_tasks.append(task_copy)
                    task_tracker.record_execution(device_id, task["task_name"])
                elif task.get("temp_account_id_storage", False) or task.get("account_id_consensus_check", False):
                    # Store empty result for account ID consensus checking
                    task_copy["ocr_result"] = ""
                    task_copy["task_name"] = f"{task['task_name']} [OCR: no Account ID detected]"
                    matched_tasks.append(task_copy)
                    task_tracker.record_execution(device_id, task["task_name"])
                elif task.get("search_for_id_pattern", False) and task.get("extract_account_id_value", False):
                    # Keep searching for ID pattern even when OCR returns nothing
                    task_copy["task_name"] = f"{task['task_name']} [🔍 Searching for ID pattern... (no text found)]"
                    matched_tasks.append(task_copy)
                    # Don't record execution to keep searching
                elif task.get("extract_orb_value", False):
                    # Keep searching for orb pattern even when OCR returns nothing
                    task_copy["task_name"] = f"{task['task_name']} [🔍 Searching for comma-formatted orbs... (no text found)]"
                    matched_tasks.append(task_copy)
                    # Don't record execution to keep searching
                else:
                    # For other tasks, treat as normal failure
                    task_copy["task_name"] = f"{task['task_name']} [No text detected]"
                    matched_tasks.append(task_copy)
                    task_tracker.record_execution(device_id, task["task_name"])
        else:
            # Original OCR text search functionality
            ocr_text = task.get("ocr_text", "")
            if not ocr_text:
                continue
            
            # Parse search texts (comma-separated)
            search_texts = [text.strip().lower() for text in ocr_text.split(",")]
            
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

async def execute_text_input(device_id: str, text: str):
    """Execute text input command with proper special character handling"""
    if not text:
        print(f"[TEXT_INPUT] {device_id} - Empty text, returning")
        return
    
    print(f"[TEXT_INPUT] {device_id} - Starting text input: {repr(text)}")
    
    # Escape special characters for ADB shell
    # Use base64 encoding for complex passwords with special characters
    import base64
    import shlex
    
    try:
        # Method 1: Try direct input with manual command format (double quotes around single quotes)
        command = f"shell input text \"'{text}'\""
        print(f"[TEXT_INPUT] {device_id} - Executing Method 1: adb -s {device_id} {command}")
        
        result = await run_adb_command(command, device_id)
        print(f"[TEXT_INPUT] {device_id} - Method 1 executed successfully, result: {result}")
        
    except Exception as e:
        print(f"[TEXT_INPUT] {device_id} - Direct method failed, trying base64 method: {e}")
        try:
            # Method 2: Base64 encoding method for complex characters
            encoded_text = base64.b64encode(text.encode('utf-8')).decode('ascii')
            command = f"shell 'echo {encoded_text} | base64 -d | input text'"
            print(f"[TEXT_INPUT] {device_id} - Executing Method 2: adb -s {device_id} {command}")
            
            result = await run_adb_command(command, device_id)
            print(f"[TEXT_INPUT] {device_id} - Method 2 executed successfully, result: {result}")
            
        except Exception as e2:
            print(f"[TEXT_INPUT] {device_id} - Base64 method failed: {e2}")
            # Method 3: Character by character input as fallback
            print(f"[TEXT_INPUT] {device_id} - Trying Method 3: character-by-character")
            for i, char in enumerate(text):
                try:
                    if char.isalnum() or char in ' .-_@':
                        char_command = f"shell input text '{char}'"
                    else:
                        # Use keycode for special characters if available
                        char_command = f"shell input text '{shlex.quote(char)}'"
                    
                    print(f"[TEXT_INPUT] {device_id} - Char {i+1}/{len(text)}: adb -s {device_id} {char_command}")
                    result = await run_adb_command(char_command, device_id)
                    print(f"[TEXT_INPUT] {device_id} - Char {i+1} executed, result: {result}")
                    await asyncio.sleep(0.05)  # Small delay between characters
                except Exception as char_e:
                    print(f"[TEXT_INPUT] {device_id} - Char {i+1} failed: {char_e}")
    
    print(f"[TEXT_INPUT] {device_id} - Text input completed")

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

async def save_screenshot_with_username(device_id: str, screenshot: np.ndarray):
    """Save screenshot with username from device state, including device numbering and cropping"""
    try:
        # Import here to avoid circular import
        from device_state_manager import device_state_manager
        
        # Get username from device state
        state = device_state_manager.get_state(device_id)
        username = state.get("UserName", "Unknown")
        
        # Get the correct device name using device_state_manager mapping
        device_name = device_state_manager._get_device_name(device_id)
        
        # Extract device number from device name (e.g., "DEVICE10" -> "10")
        device_number = "Unknown"
        if device_name.startswith("DEVICE"):
            try:
                device_number = device_name[6:]  # Remove "DEVICE" prefix
                if not device_number.isdigit():
                    device_number = "Unknown"
            except:
                device_number = "Unknown"
        
        # If username is "Unknown" or empty, also check if we have any AccountID
        if username in ["Unknown", "", None]:
            account_id = state.get("AccountID", "")
            if account_id and "ID:" in account_id:
                # Extract just the ID numbers for better naming
                id_numbers = account_id.replace("ID:", "").strip().replace(" ", "")[:6]  # Take first 6 chars
                username = f"ID{id_numbers}"
            else:
                username = "Player"
        
        # Create stock_images directory if it doesn't exist
        stock_images_dir = "stock_images"
        os.makedirs(stock_images_dir, exist_ok=True)
        
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(screenshot.astype('uint8'), 'RGB')
        
        # Crop the image to roi [160, 0, 779, 540]
        # PIL crop format is (left, top, right, bottom)
        crop_box = (160, 0, 160 + 779, 540)  # (left, top, right, bottom)
        cropped_image = pil_image.crop(crop_box)
        
        # Get current stock value for filename
        current_stock = device_state_manager.get_current_stock()
        
        # Save with stock, device number and username as filename
        filename = f"{current_stock}_{device_number}_{username}.png"
        filepath = os.path.join(stock_images_dir, filename)
        
        cropped_image.save(filepath)
        print(f"[{device_id}] Screenshot saved as: {filepath}")
        print(f"[{device_id}] Mapping: {device_id} -> {device_name} -> Stock:{current_stock} + {device_number}_{username}")
        print(f"[{device_id}] Cropped to roi [160, 0, 779, 540]")
        
    except Exception as e:
        print(f"[{device_id}] Error saving screenshot: {e}")

# Configure default cooldowns
task_tracker.set_task_cooldown("Click [Skip]", 3.0)
task_tracker.set_task_cooldown("Connection Error - Retry", 5.0)
task_tracker.set_task_cooldown("Click [OK]", 2.0)

# Export the enhanced batch check function
batch_check_pixels = batch_check_pixels_enhanced