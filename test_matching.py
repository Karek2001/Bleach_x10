#!/usr/bin/env python3
"""
Template Matching Test Tool
Visualizes template matching results for debugging and testing.
Mirrors the multi-click and sorting logic of the main project.
"""

import cv2
import numpy as np
import os
import sys
from typing import List, Tuple, Optional
from tasks.main_tasks import Main_Tasks
import tkinter as tk
from tkinter import filedialog, messagebox

# Import PixelAdvanced functions from actions.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from actions import hex_to_rgb, find_pixel_advanced_pattern

def load_template(template_path: str) -> Optional[np.ndarray]:
    """Load and convert template image"""
    if not os.path.exists(template_path):
        print(f"Template not found: {template_path}")
        return None
    
    try:
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            return None
        # Convert BGR to RGB for consistency with the main project's screenshot format
        template = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
        return template
    except Exception as e:
        print(f"Error loading template {template_path}: {e}")
        return None

# MODIFIED: Added 'sort_by_x' parameter to mirror main project's functionality
def find_template_matches(screenshot: np.ndarray, template_path: str, 
                         roi: Tuple[int, int, int, int], 
                         confidence: float = 0.9,
                         sort_by_x: bool = False) -> List[Tuple[int, int, float]]:
    """Find template matches and return positions with confidence scores"""
    template = load_template(template_path)
    if template is None:
        return []
    
    try:
        search_area = screenshot
        x_offset, y_offset = 0, 0

        # Extract ROI from screenshot if provided
        if roi:
            x, y, w, h = roi
            # Ensure ROI is within screenshot bounds
            h = min(h, screenshot.shape[0] - y)
            w = min(w, screenshot.shape[1] - x)
            search_area = screenshot[y:y+h, x:x+w]
            x_offset, y_offset = x, y
        
        if search_area.size == 0:
            return []
        
        # Template matching
        result = cv2.matchTemplate(search_area.astype(np.uint8), 
                                  template.astype(np.uint8), 
                                  cv2.TM_CCOEFF_NORMED)
        
        # Find all matches above confidence threshold
        locations = np.where(result >= confidence)
        matches = []
        template_h, template_w = template.shape[:2]
        
        # Use a fixed pixel distance for duplicate checking
        min_distance_sq = 30**2

        for pt_y, pt_x in zip(locations[0], locations[1]):
            center_x = x_offset + pt_x + template_w // 2
            center_y = y_offset + pt_y + template_h // 2
            match_confidence = result[pt_y, pt_x]
            
            # Check for duplicates
            is_duplicate = False
            for existing_x, existing_y, _ in matches:
                dist_sq = (center_x - existing_x)**2 + (center_y - existing_y)**2
                if dist_sq < min_distance_sq:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                matches.append((center_x, center_y, match_confidence))
        
        # MODIFIED: Sort matches by x-coordinate if requested (for force_multi_click)
        if sort_by_x:
            matches.sort(key=lambda m: m[0])

        return matches
        
    except Exception as e:
        print(f"Template matching error: {e}")
        return []

def draw_matches(image: np.ndarray, matches: List[Tuple[int, int, float]], 
                task_name: str, color: Tuple[int, int, int], is_sorted: bool) -> np.ndarray:
    """Draw bounding boxes and labels for matches"""
    result_img = image.copy()
    
    for i, (x, y, confidence) in enumerate(matches):
        # Draw center point
        cv2.circle(result_img, (x, y), 5, color, -1)
        
        # Draw bounding box (approximate)
        box_size = 30
        cv2.rectangle(result_img, 
                     (x - box_size, y - box_size), 
                     (x + box_size, y + box_size), 
                     color, 2)
        
        # Draw label
        sorted_tag = " [L-R]" if is_sorted else ""
        label = f"{task_name}{sorted_tag} [{i+1}]: {confidence:.3f}"
        cv2.putText(result_img, label, (x - box_size, y - box_size - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return result_img

def draw_roi(image: np.ndarray, roi: Tuple[int, int, int, int], 
            color: Tuple[int, int, int] = (255, 255, 0)) -> np.ndarray:
    """Draw ROI rectangle on image"""
    result_img = image.copy()
    x, y, w, h = roi
    cv2.rectangle(result_img, (x, y), (x + w, y + h), color, 2)
    cv2.putText(result_img, "ROI", (x, y - 10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return result_img

def draw_pixel_advanced_matches(image: np.ndarray, matches: List[Tuple[int, int]], 
                               pixels: List[str], task_name: str, 
                               color: Tuple[int, int, int]) -> np.ndarray:
    """Draw pixel pattern matches and click positions"""
    result_img = image.copy()
    
    for i, (ref_x, ref_y) in enumerate(matches):
        # Parse pixel pattern to show all pixel positions
        pattern_positions = []
        for pixel_str in pixels:
            if ',' in pixel_str:
                parts = pixel_str.split(',')
                if len(parts) == 2:
                    offset = int(parts[0])
                    pixel_x = ref_x + offset
                    pixel_y = ref_y
                    pattern_positions.append((pixel_x, pixel_y, parts[1]))  # Include color
        
        # Draw pattern pixels
        for j, (px, py, hex_color) in enumerate(pattern_positions):
            # Draw small circle for each pixel in pattern
            cv2.circle(result_img, (px, py), 3, color, -1)
            # Draw pixel number
            cv2.putText(result_img, str(j+1), (px-5, py-8), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        # Draw line connecting pattern pixels
        if len(pattern_positions) >= 2:
            for j in range(len(pattern_positions)-1):
                cv2.line(result_img, 
                        (pattern_positions[j][0], pattern_positions[j][1]),
                        (pattern_positions[j+1][0], pattern_positions[j+1][1]),
                        color, 1)
        
        # Calculate and draw click position (second pixel)
        if len(pattern_positions) >= 2:
            click_x, click_y = pattern_positions[1][0], pattern_positions[1][1]
            # Draw larger circle for click position
            cv2.circle(result_img, (click_x, click_y), 8, (0, 255, 0), 3)  # Green circle
            cv2.putText(result_img, "CLICK", (click_x-20, click_y-15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw match label
        label = f"{task_name} [{i+1}]: Pattern Match"
        cv2.putText(result_img, label, (ref_x, ref_y - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    
    return result_img

def select_image_file():
    """Open GUI file picker to select image"""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    file_path = filedialog.askopenfilename(
        title="Select Screenshot to Test",
        filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")],
        initialdir=os.getcwd()
    )
    
    root.destroy()
    return file_path

def test_template_matching():
    """Main testing function"""
    print("=" * 60)
    print("Template Matching Test Tool")
    print("=" * 60)
    
    print("Opening file picker to select a screenshot...")
    image_path = select_image_file()
    
    if not image_path:
        print("No file selected. Exiting...")
        return
    
    print(f"Selected: {image_path}")
    
    try:
        screenshot = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if screenshot is None:
            raise ValueError("Failed to load image file.")
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        print(f"Loaded image: {screenshot.shape[1]}x{screenshot.shape[0]}")
    except Exception as e:
        print(f"Error loading image: {e}")
        return
    
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
        (255, 0, 255), (0, 255, 255), (255, 128, 0), (128, 0, 255)
    ]
    
    result_img = screenshot.copy()
    total_matches_found = 0
    color_idx = 0
    
    print("\nTesting all template-based tasks from `main_tasks.py`...")
    print("-" * 60)
    
    for task in Main_Tasks:
        task_type = task.get("type")
        if task_type == "template":
            task_name = task.get("task_name", "Unknown")
            roi = task.get("roi") # A task might not have an ROI if it searches the whole screen
            confidence = task.get("confidence", 0.9)
            
            # MODIFIED: Check for the force_multi_click flag
            is_multi_click = task.get("force_multi_click", False)
            
            # MODIFIED: Handle both 'template_path' and 'template_paths'
            templates_to_check = []
            if task.get("template_path"):
                templates_to_check.append(task["template_path"])
            if task.get("template_paths"):
                templates_to_check.extend(task["template_paths"])

            if not templates_to_check:
                continue

            multi_click_tag = "[Sorted L-R]" if is_multi_click else ""
            print(f"Testing: {task_name} {multi_click_tag}")
            
            all_matches_for_task = []
            for template_path in templates_to_check:
                print(f"  - Template: {template_path}")
                
                # Call the updated find function, passing the sorting flag
                matches = find_template_matches(screenshot, template_path, roi, confidence, sort_by_x=is_multi_click)
                if matches:
                    all_matches_for_task.extend(matches)

            if all_matches_for_task:
                # Re-sort if multiple templates contributed matches for a multi-click task
                if is_multi_click:
                    all_matches_for_task.sort(key=lambda m: m[0])

                print(f"  ✓ Found {len(all_matches_for_task)} total matches for this task.")
                for i, (x, y, conf) in enumerate(all_matches_for_task):
                    print(f"    Match {i+1}: ({x}, {y}) confidence={conf:.3f}")
                
                color = colors[color_idx % len(colors)]
                result_img = draw_matches(result_img, all_matches_for_task, task_name, color, is_multi_click)
                if roi:
                    result_img = draw_roi(result_img, roi, color)
                
                total_matches_found += len(all_matches_for_task)
                color_idx += 1
            else:
                print(f"  ✗ No matches found for this task.")
            
            print()
        
    
    print(f"Total matches found across all tasks: {total_matches_found}")
    
    if total_matches_found > 0:
        print("\nDisplaying results... (Press any key in the image window to close)")
        
        display_img = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR)
        
        h, w = display_img.shape[:2]
        if w > 1200 or h > 800:
            scale = min(1200/w, 800/h)
            new_w, new_h = int(w * scale), int(h * scale)
            display_img = cv2.resize(display_img, (new_w, new_h))
            print(f"Resized for display: {new_w}x{new_h}")
        
        cv2.imshow("Template Matching Results", display_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        root = tk.Tk()
        root.withdraw()
        if messagebox.askyesno("Save Result", "Do you want to save the result image?"):
            output_path = filedialog.asksaveasfilename(
                title="Save Result Image",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png")],
                initialname=f"test_result_{os.path.basename(image_path)}"
            )
            if output_path:
                cv2.imwrite(output_path, cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR))
                print(f"Result saved to: {output_path}")
        root.destroy()
    else:
        messagebox.showinfo("No Matches", "No template matches were found in the selected image.")

def main():
    """Main function with continuous testing loop"""
    try:
        while True:
            test_template_matching()
            root = tk.Tk()
            root.withdraw()
            if not messagebox.askyesno("Continue", "Test another image?"):
                break
            root.destroy()
    except KeyboardInterrupt:
        print("\nExiting.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()