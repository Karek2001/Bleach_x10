#!/usr/bin/env python3
"""
Template Matching Test Tool
Visualizes template matching results for debugging and testing.
Fixed version without missing imports.
"""

import cv2
import numpy as np
import os
import sys
from typing import List, Tuple, Optional
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import settings
try:
    import settings
except ImportError:
    # Fallback if settings not available
    class MockSettings:
        SPAM_LOGS = True  # Default to True for test file
    settings = MockSettings()

# Import from tasks
try:
    from tasks import (
        StoryMode_Tasks, Restarting_Tasks, Shared_Tasks, Switcher_Tasks,
        GUILD_TUTORIAL_TASKS, Guild_Rejoin, Sell_Characters,
        HardStory_Tasks, SideStory, SubStories, SubStories_check
    )
    
    # Combine all task lists into a dictionary for easy access
    ALL_TASK_CATEGORIES = {
        "Story Mode Tasks": StoryMode_Tasks,
        "Restarting Tasks": Restarting_Tasks,
        "Shared Tasks": Shared_Tasks,
        "Switcher Tasks": Switcher_Tasks,
        "Guild Tutorial Tasks": GUILD_TUTORIAL_TASKS,
        "Guild Rejoin": Guild_Rejoin,
        "Sell Characters": Sell_Characters,
        "Hard Story Tasks": HardStory_Tasks,
        "Side Story": SideStory,
        "Sub Stories": SubStories,
        "Sub Stories Check": SubStories_check
    }
except ImportError as e:
    print(f"Warning: Could not import tasks: {e}")
    print("Using empty task categories")
    ALL_TASK_CATEGORIES = {"Main Tasks": []}

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Converts a hex color string to an (R, G, B) tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def check_pixel_task(screenshot: np.ndarray, task: dict) -> bool:
    """Check if a pixel task matches the screenshot"""
    search_array = task.get("search_array", [])
    if len(search_array) < 2:
        return False
    
    # Check all pixel-color pairs
    for i in range(0, len(search_array), 2):
        if i + 1 >= len(search_array):
            break
            
        coords_str = search_array[i]
        hex_color = search_array[i + 1]
        
        try:
            x, y = map(int, coords_str.split(','))
            expected_rgb = hex_to_rgb(hex_color)
            
            # Check bounds
            if 0 <= y < screenshot.shape[0] and 0 <= x < screenshot.shape[1]:
                pixel_color = screenshot[y, x]
                if not np.array_equal(pixel_color, np.array(expected_rgb)):
                    return False
            else:
                return False
        except (ValueError, IndexError):
            return False
    
    return True

def check_pixel_one_or_more_task(screenshot: np.ndarray, task: dict) -> bool:
    """Check if a Pixel-OneOrMoreMatched task has any matching pairs"""
    pixel_values = task.get("pixel-values", [])
    if len(pixel_values) < 4:
        return False
    
    # Check consecutive pairs
    for i in range(0, len(pixel_values) - 3, 2):
        try:
            coords1_str = pixel_values[i]
            color1 = pixel_values[i + 1]
            coords2_str = pixel_values[i + 2] 
            color2 = pixel_values[i + 3]
            
            x1, y1 = map(int, coords1_str.split(','))
            x2, y2 = map(int, coords2_str.split(','))
            
            expected_rgb1 = hex_to_rgb(color1)
            expected_rgb2 = hex_to_rgb(color2)
            
            # Check bounds and colors
            if (0 <= y1 < screenshot.shape[0] and 0 <= x1 < screenshot.shape[1] and
                0 <= y2 < screenshot.shape[0] and 0 <= x2 < screenshot.shape[1]):
                
                pixel_color1 = screenshot[y1, x1]
                pixel_color2 = screenshot[y2, x2]
                
                if (np.array_equal(pixel_color1, np.array(expected_rgb1)) and
                    np.array_equal(pixel_color2, np.array(expected_rgb2))):
                    return True
        except (ValueError, IndexError):
            continue
    
    return False

def load_template(template_path: str) -> Optional[np.ndarray]:
    """Load and convert template image"""
    # Convert relative paths to absolute paths from project root
    if not os.path.isabs(template_path):
        project_root = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(project_root, template_path)
    
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
        
        # Sort matches by x-coordinate if requested
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

def draw_pixel_matches(image: np.ndarray, task: dict, task_name: str, 
                      color: Tuple[int, int, int]) -> np.ndarray:
    """Draw pixel detection points and labels"""
    result_img = image.copy()
    
    if task.get("type") == "pixel":
        search_array = task.get("search_array", [])
        for i in range(0, len(search_array), 2):
            if i + 1 >= len(search_array):
                break
            try:
                coords_str = search_array[i]
                hex_color = search_array[i + 1]
                x, y = map(int, coords_str.split(','))
                
                # Draw pixel point
                cv2.circle(result_img, (x, y), 3, color, -1)
                cv2.circle(result_img, (x, y), 8, color, 2)
                
                # Draw label with expected color
                label = f"{task_name} [{i//2+1}]: {hex_color}"
                cv2.putText(result_img, label, (x + 10, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            except (ValueError, IndexError):
                continue
    
    elif task.get("type") == "Pixel-OneOrMoreMatched":
        pixel_values = task.get("pixel-values", [])
        for i in range(0, len(pixel_values), 2):
            if i + 1 >= len(pixel_values):
                break
            try:
                coords_str = pixel_values[i]
                hex_color = pixel_values[i + 1]
                x, y = map(int, coords_str.split(','))
                
                # Draw pixel point
                cv2.circle(result_img, (x, y), 3, color, -1)
                cv2.circle(result_img, (x, y), 8, color, 2)
                
                # Draw label
                label = f"{task_name} [{i//2+1}]: {hex_color}"
                cv2.putText(result_img, label, (x + 10, y - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
            except (ValueError, IndexError):
                continue
    
    return result_img

def display_results_tkinter(image: np.ndarray):
    """Display results using Tkinter instead of OpenCV"""
    try:
        # Create new window
        result_window = tk.Toplevel()
        result_window.title("Template Matching Results")
        result_window.configure(bg="#2E2E2E")
        result_window.geometry("1400x900")
        
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(image.astype('uint8'))
        
        # Scale image if too large
        max_width, max_height = 1200, 800
        if pil_image.width > max_width or pil_image.height > max_height:
            scale_factor = min(max_width / pil_image.width, max_height / pil_image.height)
            new_size = (int(pil_image.width * scale_factor), int(pil_image.height * scale_factor))
            pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(pil_image)
        
        # Create canvas
        canvas = tk.Canvas(result_window, width=pil_image.width, height=pil_image.height, bg="white")
        canvas.pack(pady=10)
        
        # Display image
        canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        
        # Instructions
        instructions = tk.Label(result_window, 
                               text="Template matching results displayed. Close window when done.",
                               font=("Arial", 12), bg="#2E2E2E", fg="#FFFFFF")
        instructions.pack(pady=10)
        
        # Close button
        close_btn = tk.Button(result_window, text="Close", command=result_window.destroy,
                             font=("Arial", 12), bg="#555555", fg="#FFFFFF")
        close_btn.pack(pady=10)
        
        # Keep reference to photo to prevent garbage collection
        result_window.photo = photo
        
        # Make window modal and wait for it to close
        result_window.transient()
        result_window.grab_set()
        result_window.wait_window()
        
    except Exception as e:
        print(f"Error displaying results: {e}")
        # Fallback: save image instead
        try:
            pil_image = Image.fromarray(image.astype('uint8'))
            pil_image.save('template_matching_results.png')
            print("Results saved as 'template_matching_results.png'")
        except Exception as save_e:
            print(f"Could not save results: {save_e}")

def draw_roi(image: np.ndarray, roi: Tuple[int, int, int, int], 
            color: Tuple[int, int, int] = (255, 255, 0)) -> np.ndarray:
    """Draw ROI rectangle on image"""
    result_img = image.copy()
    x, y, w, h = roi
    cv2.rectangle(result_img, (x, y), (x + w, y + h), color, 2)
    cv2.putText(result_img, "ROI", (x, y - 10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return result_img

def run_template_matching_browser():
    """Run template matching with integrated image browser"""
    root = tk.Tk()
    root.title("Template Matching Tool - /mnt/storagebox")
    root.geometry("1600x900")
    root.configure(bg="#2E2E2E")
    
    # Directory for images
    image_dir = "/mnt/storagebox"
    
    # Variables
    selected_buttons = set()
    
    # Header
    header_label = tk.Label(root, text="Template Matching Tool - Click any image to process", 
                           font=("Helvetica", 14, "bold"), 
                           bg="#2E2E2E", fg="#FFFFFF", pady=10)
    header_label.pack()
    
    # Instructions
    instructions = tk.Label(root, 
                           text="Click on any image below to immediately run template matching. Green buttons show processed images.",
                           font=("Arial", 10), bg="#2E2E2E", fg="#CCCCCC")
    instructions.pack(pady=5)
    
    # Grid layout for images
    list_frame = tk.Frame(root, bg="#2E2E2E")
    list_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create canvas and scrollbar for grid
    list_canvas = tk.Canvas(list_frame, bg="#3C3C3C", highlightthickness=0)
    scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=list_canvas.yview)
    scrollable_frame = tk.Frame(list_canvas, bg="#3C3C3C")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all"))
    )
    
    list_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    list_canvas.configure(yscrollcommand=scrollbar.set)
    
    # Bind mouse wheel scrolling
    def _on_mousewheel(event):
        list_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    list_canvas.bind("<MouseWheel>", _on_mousewheel)
    scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
    
    list_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def process_image(image_path, button):
        """Process the selected image immediately."""
        print(f"\n{'='*60}")
        print(f"Processing: {os.path.basename(image_path)}")
        print(f"{'='*60}")
        
        # Highlight button
        button.configure(bg="#00AA00")
        selected_buttons.add(button)
        
        # Process the image
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
        
        # Process each task category
        for category_name, task_list in ALL_TASK_CATEGORIES.items():
            if not task_list:  # Skip empty task lists
                continue
                
            print(f"\n{'='*60}")
            print(f"TESTING CATEGORY: {category_name}")
            print(f"{'='*60}")
            
            # Process each task in the category
            for task in task_list:
                task_type = task.get("type", "pixel")
                if task_type not in ["template", "pixel", "Pixel-OneOrMoreMatched"]:
                    continue
                
                task_name = task.get("task_name", "Unknown Task")
                
                if task_type == "template":
                    template_path = task.get("template_path")
                    roi = task.get("roi")
                    confidence = 0.9
                    
                    if settings.SPAM_LOGS:
                        print(f"\nTesting: {task_name} [{category_name}] [TEMPLATE]")
                        print(f"  Template: {template_path}")
                        print(f"  ROI: {roi}")
                    
                    if not template_path:
                        if settings.SPAM_LOGS:
                            print(f"  ✗ No template path specified")
                        continue
                    
                    # Convert relative paths to absolute paths from project root
                    if not os.path.isabs(template_path):
                        project_root = os.path.dirname(os.path.abspath(__file__))
                        full_template_path = os.path.join(project_root, template_path)
                    else:
                        full_template_path = template_path
                    
                    if not os.path.exists(full_template_path):
                        if settings.SPAM_LOGS:
                            print(f"  ✗ Template not found: {full_template_path}")
                        continue
                    
                    is_multi_click = task.get("multi_click", False)
                    all_matches_for_task = find_template_matches(screenshot, template_path, roi, confidence, is_multi_click)
                    
                    if all_matches_for_task:
                        if settings.SPAM_LOGS:
                            print(f"  ✓ Found {len(all_matches_for_task)} matches at confidence {confidence}")
                            for i, (x, y, c) in enumerate(all_matches_for_task):
                                print(f"    Match {i+1}: ({x}, {y}) confidence: {c:.3f}")
                        
                        color = colors[color_idx % len(colors)]
                        result_img = draw_matches(result_img, all_matches_for_task, task_name, color, is_multi_click)
                        if roi:
                            result_img = draw_roi(result_img, roi, color)
                        
                        total_matches_found += len(all_matches_for_task)
                        color_idx += 1
                    else:
                        if settings.SPAM_LOGS:
                            print(f"  ✗ No matches found at confidence {confidence}")
                
                elif task_type == "pixel":
                    search_array = task.get("search_array", [])
                    
                    if settings.SPAM_LOGS:
                        print(f"\nTesting: {task_name} [{category_name}] [PIXEL]")
                        print(f"  Search Array: {len(search_array)//2} pixel-color pairs")
                        for i in range(0, len(search_array), 2):
                            if i + 1 < len(search_array):
                                print(f"    Pixel {i//2+1}: {search_array[i]} -> {search_array[i+1]}")
                    
                    pixel_match = check_pixel_task(screenshot, task)
                    
                    if pixel_match:
                        if settings.SPAM_LOGS:
                            print(f"  ✓ All pixels match expected colors")
                        
                        color = colors[color_idx % len(colors)]
                        result_img = draw_pixel_matches(result_img, task, task_name, color)
                        total_matches_found += 1
                        color_idx += 1
                    else:
                        if settings.SPAM_LOGS:
                            print(f"  ✗ Pixel colors do not match")
                
                elif task_type == "Pixel-OneOrMoreMatched":
                    pixel_values = task.get("pixel-values", [])
                    
                    if settings.SPAM_LOGS:
                        print(f"\nTesting: {task_name} [{category_name}] [PIXEL-ONE-OR-MORE]")
                        print(f"  Pixel Values: {len(pixel_values)//2} pixel-color pairs")
                        for i in range(0, len(pixel_values), 2):
                            if i + 1 < len(pixel_values):
                                print(f"    Pixel {i//2+1}: {pixel_values[i]} -> {pixel_values[i+1]}")
                    
                    pixel_match = check_pixel_one_or_more_task(screenshot, task)
                    
                    if pixel_match:
                        if settings.SPAM_LOGS:
                            print(f"  ✓ At least one pixel pair matches")
                        
                        color = colors[color_idx % len(colors)]
                        result_img = draw_pixel_matches(result_img, task, task_name, color)
                        total_matches_found += 1
                        color_idx += 1
                    else:
                        if settings.SPAM_LOGS:
                            print(f"  ✗ No pixel pairs match")
        
        print(f"\nTotal matches found: {total_matches_found}")
        
        # Display results
        if True:  # Always show results
            print("Displaying results...")
            display_results_tkinter(result_img)
    
    # Populate image grid
    try:
        # Get image files only from the main shared directory
        image_files = []
        try:
            files = os.listdir(image_dir)
            for file in files:
                full_path = os.path.join(image_dir, file)
                if os.path.isfile(full_path) and file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    image_files.append((full_path, file))
        except OSError:
            pass
        
        if not image_files:
            label = tk.Label(scrollable_frame, text="No images found in the directory.", 
                           font=("Arial", 10), bg="#3C3C3C", fg="#FFFFFF", padx=10, pady=10)
            label.pack()
        else:
            # Sort by filename
            image_files.sort(key=lambda x: x[1].lower())
            
            # Create grid layout - 4 columns
            columns = 4
            for i, (full_path, filename) in enumerate(image_files):
                row = i // columns
                col = i % columns
                
                # Create a frame for each image button
                btn_frame = tk.Frame(scrollable_frame, bg="#3C3C3C")
                btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                
                # Create button with truncated filename
                display_name = filename if len(filename) <= 30 else "..." + filename[-27:]
                btn = tk.Button(btn_frame, text=display_name, font=("Arial", 9),
                               bg="#555555", fg="#FFFFFF", relief="flat", 
                               padx=6, pady=3, width=30, anchor="w")
                btn.configure(command=lambda p=full_path, b=btn: process_image(p, b))
                btn.pack(fill="x")
            
            # Configure grid column weights
            for col in range(columns):
                scrollable_frame.grid_columnconfigure(col, weight=1)
                
    except FileNotFoundError:
        label = tk.Label(scrollable_frame, 
                       text=f"Error: Directory not found:\n{image_dir}", 
                       font=("Arial", 10), bg="#3C3C3C", fg="#FF5555", padx=10, pady=10)
        label.pack()
    
    root.mainloop()

def test_template_matching():
    """Main testing function - now just launches the browser"""
    print("=" * 60)
    print("Template Matching Test Tool")
    print("=" * 60)
    
    print("Opening template matching browser...")
    run_template_matching_browser()

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