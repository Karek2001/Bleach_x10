import cv2
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import os
import subprocess
import platform

# --- ROI Selector using pure Tkinter (no OpenCV GUI dependency) ---

def copy_to_clipboard(text):
    """A helper function to copy text to the clipboard - Linux/Wayland compatible."""
    try:
        # Try Linux clipboard tools first (avoids Tkinter conflicts)
        if platform.system() == "Linux":
            # Check if we're in Wayland environment first
            if os.environ.get('WAYLAND_DISPLAY') or os.environ.get('XDG_SESSION_TYPE') == 'wayland':
                # Try wl-copy for Wayland (Sway, GNOME Wayland, etc.)
                try:
                    subprocess.run(['wl-copy'], input=text.encode(), check=True)
                    print(f"\nSUCCESS: Copied to clipboard (Wayland)!")
                    print(f"'{text}'")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
            
            # Try X11 clipboard tools
            # Try xclip first
            try:
                subprocess.run(['xclip', '-selection', 'clipboard'], 
                             input=text.encode(), check=True)
                print(f"\nSUCCESS: Copied to clipboard (X11)!")
                print(f"'{text}'")
                return
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to xsel
                try:
                    subprocess.run(['xsel', '--clipboard', '--input'], 
                                 input=text.encode(), check=True)
                    print(f"\nSUCCESS: Copied to clipboard (X11)!")
                    print(f"'{text}'")
                    return
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
        
        # Fallback to Tkinter (Windows/Mac or Linux without clipboard tools)
        # Use a more careful approach to avoid conflicts
        temp_root = tk.Tk()
        temp_root.withdraw()
        temp_root.clipboard_clear()
        temp_root.clipboard_append(text)
        temp_root.update()
        temp_root.quit()
        temp_root.destroy()
        print(f"\nSUCCESS: Copied to clipboard!")
        print(f"'{text}'")
        
    except Exception as e:
        print(f"\nWARNING: Could not copy to clipboard: {e}")
        print(f"ROI coordinates: {text}")
        print("Please copy manually.")




def launch_roi_editor(image_path):
    """Launches ROI selection directly in the main window."""
    print(f"\n--- ROI Selection Mode ---")
    print(f"Image: {image_path}")
    print("Click and drag on the image to select ROI")
    print("ROI coordinates will be printed and copied to clipboard")
    print("-----------------------------")


class ImageSelectorApp:
    """The main GUI application to browse and select an image."""
    def __init__(self, root, image_dir):
        self.root = root
        self.image_dir = image_dir
        self.root.title("Screenshot Selector")
        self.root.geometry("1600x900")
        
        # ROI selection variables
        self.current_image_path = None
        self.original_image = None
        self.display_image = None
        self.scale_factor = 1.0
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.roi_mode = False

        # --- Styling ---
        self.root.configure(bg="#2E2E2E")
        self.header_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.list_font = font.Font(family="Helvetica", size=10)
        
        # --- Layout ---
        header_label = tk.Label(self.root, text="Select a Screenshot to Analyze", font=self.header_font, bg="#2E2E2E", fg="#FFFFFF", pady=10)
        header_label.pack()

        # --- Canvas for image preview - optimized for 960x540 images
        self.canvas = tk.Canvas(self.root, width=960, height=540, bg="lightgray")
        self.canvas.pack(pady=10)
        
        # Bind mouse events for ROI selection
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # --- Grid layout for screenshots with scrolling ---
        list_frame = tk.Frame(self.root, bg="#2E2E2E")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar for grid
        self.list_canvas = tk.Canvas(list_frame, bg="#3C3C3C", highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.list_canvas.yview)
        self.scrollable_frame = tk.Frame(self.list_canvas, bg="#3C3C3C")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all"))
        )

        self.list_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.list_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel scrolling
        self.list_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)

        self.list_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Populate the grid ---
        self.populate_image_grid()

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.list_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def populate_image_grid(self):
        """Scans the directory and populates the GUI with image files in a grid layout."""
        try:
            image_files = [f for f in os.listdir(self.image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        except FileNotFoundError:
            label = tk.Label(self.scrollable_frame, text=f"Error: Directory not found:\n{self.image_dir}", 
                           font=self.list_font, bg="#3C3C3C", fg="#FF5555", padx=10, pady=10)
            label.pack()
            return

        if not image_files:
            label = tk.Label(self.scrollable_frame, text="No images found in the directory.", 
                           font=self.list_font, bg="#3C3C3C", fg="#FFFFFF", padx=10, pady=10)
            label.pack()
            return

        # Create grid layout - 4 columns
        columns = 4
        for i, filename in enumerate(sorted(image_files, reverse=True)):
            path = os.path.join(self.image_dir, filename)
            row = i // columns
            col = i % columns
            
            # Create a frame for each image button
            btn_frame = tk.Frame(self.scrollable_frame, bg="#3C3C3C")
            btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            # Create button with truncated filename
            display_name = filename if len(filename) <= 25 else filename[:22] + "..."
            btn = tk.Button(btn_frame, text=display_name, font=self.list_font,
                           command=lambda p=path: self.select_image(p),
                           bg="#555555", fg="#FFFFFF", relief="flat", 
                           padx=8, pady=4, width=25, anchor="w")
            btn.pack(fill="x")
            
        # Configure grid column weights for equal distribution
        for col in range(columns):
            self.scrollable_frame.grid_columnconfigure(col, weight=1)

    def display_image_preview(self, image_path):
        """Display a preview of the selected image in the canvas."""
        try:
            # Load the image
            self.original_image = Image.open(image_path)
            
            # For 960x540 images, display at actual size or scale down if larger
            canvas_width, canvas_height = 960, 540
            self.scale_factor = min(1.0, min(canvas_width / self.original_image.width, 
                                           canvas_height / self.original_image.height))
            
            new_width = int(self.original_image.width * self.scale_factor)
            new_height = int(self.original_image.height * self.scale_factor)
            
            self.display_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage and display
            self.photo = ImageTk.PhotoImage(self.display_image)
            self.canvas.delete("all")  # Clear previous image
            self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.photo)
            
        except Exception as e:
            print(f"Error loading image preview: {e}")

    def select_image(self, image_path):
        """Called when an image is selected from the list."""
        print(f"Image selected: {image_path}")
        self.current_image_path = image_path
        
        # Load and display the image in the canvas
        self.display_image_preview(image_path)
        
        # Enable ROI selection mode
        self.roi_mode = True
        print(f"\n--- ROI Selection Mode ---")
        print(f"Click and drag on the image to select ROI")
        print(f"ROI coordinates will be printed and copied to clipboard")
        print(f"-----------------------------")

    def on_canvas_click(self, event):
        """Handle mouse click on canvas - start ROI selection."""
        if not self.roi_mode or not self.original_image:
            return
            
        self.start_x = event.x
        self.start_y = event.y
        
        # Remove previous rectangle if exists
        if self.rect_id:
            self.canvas.delete(self.rect_id)

    def on_canvas_drag(self, event):
        """Handle mouse drag on canvas - update rectangle."""
        if not self.roi_mode or not self.original_image or self.start_x is None:
            return
            
        # Remove previous rectangle
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        
        # Draw new rectangle
        self.rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y,
            outline='red', width=2
        )

    def on_canvas_release(self, event):
        """Handle mouse release on canvas - finalize ROI selection."""
        if not self.roi_mode or not self.original_image or self.start_x is None:
            return
            
        end_x, end_y = event.x, event.y
        
        # Calculate canvas center offset
        canvas_width, canvas_height = 960, 540
        image_x_offset = (canvas_width - self.display_image.width) // 2
        image_y_offset = (canvas_height - self.display_image.height) // 2
        
        # Adjust coordinates relative to image position
        adj_start_x = self.start_x - image_x_offset
        adj_start_y = self.start_y - image_y_offset
        adj_end_x = end_x - image_x_offset
        adj_end_y = end_y - image_y_offset
        
        # Calculate ROI coordinates in original image scale
        x_coord = int(min(adj_start_x, adj_end_x) / self.scale_factor)
        y_coord = int(min(adj_start_y, adj_end_y) / self.scale_factor)
        width = int(abs(adj_start_x - adj_end_x) / self.scale_factor)
        height = int(abs(adj_start_y - adj_end_y) / self.scale_factor)
        
        # Ensure coordinates are within image bounds
        x_coord = max(0, min(x_coord, self.original_image.width - 1))
        y_coord = max(0, min(y_coord, self.original_image.height - 1))
        width = min(width, self.original_image.width - x_coord)
        height = min(height, self.original_image.height - y_coord)
        
        roi_string = f'"roi": [{x_coord}, {y_coord}, {width}, {height}]'
        
        print("\n--- ROI Coordinates ---")
        print(f"Copy this into your config.json:")
        print(roi_string)
        print("-----------------------")
        copy_to_clipboard(roi_string)


if __name__ == "__main__":
    # Define the default directory for screenshots
    default_directory = "/mnt/storagebox"

    # Create and run the main GUI application
    main_root = tk.Tk()
    app = ImageSelectorApp(main_root, default_directory)
    main_root.mainloop()

    print("\nGUI closed. Application finished.")
