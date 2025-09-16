import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import os

class ImageCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Cropper")
        self.root.geometry("1600x900")
        self.root.configure(bg="#2E2E2E")
        
        # Directory for images
        self.image_dir = "/mnt/storagebox/LevelUp_Characters"
        self.output_dir = os.path.join(self.image_dir, "output")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Variables
        self.current_image_path = None
        self.original_image = None
        self.display_image = None
        self.scale_factor = 1.0
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        self.crop_mode = False
        self.tooltip = None
        self.current_filename = None
        self.selected_button = None
        
        # Setup UI
        self.setup_ui()
        self.populate_image_grid()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Header
        header_label = tk.Label(self.root, text="Select an Image to Crop", 
                               font=("Helvetica", 14, "bold"), 
                               bg="#2E2E2E", fg="#FFFFFF", pady=10)
        header_label.pack()
        
        # Canvas for image display
        self.canvas = tk.Canvas(self.root, width=960, height=540, bg="lightgray")
        self.canvas.pack(pady=10)
        
        # Bind mouse events for crop selection
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_hover)
        self.canvas.bind("<Leave>", self.hide_tooltip)
        
        # Instructions
        instructions = tk.Label(self.root, 
                               text="1. Select an image from below  2. Click and drag to select crop area  3. Crop will be saved automatically",
                               font=("Arial", 10), bg="#2E2E2E", fg="#CCCCCC")
        instructions.pack(pady=5)
        
        # Grid layout for screenshots
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
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        self.list_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def populate_image_grid(self):
        """Populate the grid with image files."""
        try:
            image_files = [f for f in os.listdir(self.image_dir) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        except FileNotFoundError:
            label = tk.Label(self.scrollable_frame, 
                           text=f"Error: Directory not found:\n{self.image_dir}", 
                           font=("Arial", 10), bg="#3C3C3C", fg="#FF5555", padx=10, pady=10)
            label.pack()
            return
        
        if not image_files:
            label = tk.Label(self.scrollable_frame, text="No images found in the directory.", 
                           font=("Arial", 10), bg="#3C3C3C", fg="#FFFFFF", padx=10, pady=10)
            label.pack()
            return
        
        # Create grid layout - 4 columns
        columns = 4
        for i, filename in enumerate(sorted(image_files)):
            path = os.path.join(self.image_dir, filename)
            row = i // columns
            col = i % columns
            
            # Create a frame for each image button
            btn_frame = tk.Frame(self.scrollable_frame, bg="#3C3C3C")
            btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            # Create button with truncated filename
            display_name = filename if len(filename) <= 25 else filename[:22] + "..."
            btn = tk.Button(btn_frame, text=display_name, font=("Arial", 10),
                           command=lambda p=path, b=None: self.select_image(p, b),
                           bg="#555555", fg="#FFFFFF", relief="flat", 
                           padx=8, pady=4, width=25, anchor="w")
            btn.pack(fill="x")
            
            # Store button reference for later color changes
            btn.configure(command=lambda p=path, b=btn: self.select_image(p, b))
        
        # Configure grid column weights
        for col in range(columns):
            self.scrollable_frame.grid_columnconfigure(col, weight=1)
    
    def select_image(self, image_path, button):
        """Load and display selected image."""
        print(f"Image selected: {image_path}")
        
        # Don't reset previous button color - keep it green to show what was processed
        # Just highlight current button
        button.configure(bg="#00AA00")  # Green color for selected
        self.selected_button = button
        
        self.current_image_path = image_path
        self.current_filename = os.path.basename(image_path)
        self.display_image_preview(image_path)
        self.crop_mode = True
        print("Crop mode enabled - click and drag to select area to crop")
    
    def display_image_preview(self, image_path):
        """Display the selected image in the canvas."""
        try:
            # Load the image
            self.original_image = Image.open(image_path)
            
            # Scale image to fit canvas
            canvas_width, canvas_height = 960, 540
            self.scale_factor = min(1.0, min(canvas_width / self.original_image.width, 
                                           canvas_height / self.original_image.height))
            
            new_width = int(self.original_image.width * self.scale_factor)
            new_height = int(self.original_image.height * self.scale_factor)
            
            self.display_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage and display
            self.photo = ImageTk.PhotoImage(self.display_image)
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.photo)
            
        except Exception as e:
            print(f"Error loading image: {e}")
            messagebox.showerror("Error", f"Could not load image: {e}")
    
    def on_canvas_click(self, event):
        """Handle mouse click - start crop selection."""
        if not self.crop_mode or not self.original_image:
            return
        
        self.start_x = event.x
        self.start_y = event.y
        
        # Remove previous rectangle
        if self.rect_id:
            self.canvas.delete(self.rect_id)
    
    def on_canvas_drag(self, event):
        """Handle mouse drag - update crop rectangle."""
        if not self.crop_mode or not self.original_image or self.start_x is None:
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
        """Handle mouse release - perform crop and save."""
        if not self.crop_mode or not self.original_image or self.start_x is None:
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
        
        # Calculate crop coordinates in original image scale
        x1 = int(min(adj_start_x, adj_end_x) / self.scale_factor)
        y1 = int(min(adj_start_y, adj_end_y) / self.scale_factor)
        x2 = int(max(adj_start_x, adj_end_x) / self.scale_factor)
        y2 = int(max(adj_start_y, adj_end_y) / self.scale_factor)
        
        # Ensure coordinates are within image bounds
        x1 = max(0, min(x1, self.original_image.width - 1))
        y1 = max(0, min(y1, self.original_image.height - 1))
        x2 = max(x1 + 1, min(x2, self.original_image.width))
        y2 = max(y1 + 1, min(y2, self.original_image.height))
        
        # Check if crop area is valid
        if x2 - x1 < 5 or y2 - y1 < 5:
            messagebox.showwarning("Invalid Selection", "Crop area too small. Please select a larger area.")
            return
        
        # Perform crop
        self.crop_and_save(x1, y1, x2, y2)
    
    def crop_and_save(self, x1, y1, x2, y2):
        """Crop the image and save with user-specified name."""
        try:
            # Crop the image
            cropped_image = self.original_image.crop((x1, y1, x2, y2))
            
            # Ask user for filename
            filename = simpledialog.askstring(
                "Save Cropped Image", 
                "Enter filename (without extension):"
            )
            
            if not filename:
                return
            
            # Ensure .png extension
            if not filename.endswith('.png'):
                filename += '.png'
            
            # Save path to output directory
            save_path = os.path.join(self.output_dir, filename)
            
            # Check if file exists
            if os.path.exists(save_path):
                if not messagebox.askyesno("File Exists", f"File '{filename}' already exists. Overwrite?"):
                    return
            
            # Save the cropped image
            cropped_image.save(save_path, 'PNG')
            
            print(f"Cropped image saved as: {save_path}")
            messagebox.showinfo("Success", f"Cropped image saved as:\n{filename}")
            
            # Refresh the image grid to show the new file
            self.refresh_image_grid()
            
        except Exception as e:
            print(f"Error saving cropped image: {e}")
            messagebox.showerror("Error", f"Could not save cropped image: {e}")
    
    def refresh_image_grid(self):
        """Refresh the image grid to show newly saved files."""
        # Clear existing grid
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Repopulate
        self.populate_image_grid()
    
    def on_canvas_hover(self, event):
        """Show tooltip with current image filename when hovering over canvas."""
        if self.crop_mode and self.current_filename:
            self.show_tooltip(event.x_root, event.y_root, f"Current Image: {self.current_filename}")
    
    def show_tooltip(self, x, y, text):
        """Show tooltip at specified coordinates."""
        self.hide_tooltip()  # Hide any existing tooltip
        
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x+10}+{y+10}")
        
        label = tk.Label(self.tooltip, text=text, 
                        background="#FFFFE0", foreground="#000000",
                        relief="solid", borderwidth=1,
                        font=("Arial", 9))
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide the tooltip."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageCropper(root)
    root.mainloop()
