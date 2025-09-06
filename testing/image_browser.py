import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

class ImageBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Browser - /home/karek/Downloads/shared")
        self.root.geometry("1600x900")
        self.root.configure(bg="#2E2E2E")
        
        # Directory for images
        self.image_dir = "/home/karek/Downloads/shared"
        
        # Variables
        self.current_image_path = None
        self.original_image = None
        self.display_image = None
        self.scale_factor = 1.0
        self.selected_buttons = set()  # Track selected buttons
        
        # Setup UI
        self.setup_ui()
        self.populate_image_grid()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Header
        header_label = tk.Label(self.root, text="Browse Images in /home/karek/Downloads/shared", 
                               font=("Helvetica", 14, "bold"), 
                               bg="#2E2E2E", fg="#FFFFFF", pady=10)
        header_label.pack()
        
        # Canvas for image display - optimized for 960x540 images
        self.canvas = tk.Canvas(self.root, width=960, height=540, bg="lightgray")
        self.canvas.pack(pady=10)
        
        # Instructions
        instructions = tk.Label(self.root, 
                               text="Click on any image below to view it. Green buttons show images you've viewed.",
                               font=("Arial", 10), bg="#2E2E2E", fg="#CCCCCC")
        instructions.pack(pady=5)
        
        # Grid layout for images
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
            # Get all image files recursively
            image_files = []
            for root, dirs, files in os.walk(self.image_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        full_path = os.path.join(root, file)
                        # Get relative path for display
                        rel_path = os.path.relpath(full_path, self.image_dir)
                        image_files.append((full_path, rel_path))
            
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
        
        # Sort by filename
        image_files.sort(key=lambda x: x[1].lower())
        
        # Create grid layout - 4 columns
        columns = 4
        for i, (full_path, rel_path) in enumerate(image_files):
            row = i // columns
            col = i % columns
            
            # Create a frame for each image button
            btn_frame = tk.Frame(self.scrollable_frame, bg="#3C3C3C")
            btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            # Create button with truncated filename
            display_name = rel_path if len(rel_path) <= 30 else "..." + rel_path[-27:]
            btn = tk.Button(btn_frame, text=display_name, font=("Arial", 9),
                           command=lambda p=full_path, b=None: self.select_image(p, b),
                           bg="#555555", fg="#FFFFFF", relief="flat", 
                           padx=6, pady=3, width=30, anchor="w")
            btn.pack(fill="x")
            
            # Store button reference for later color changes
            btn.configure(command=lambda p=full_path, b=btn: self.select_image(p, b))
        
        # Configure grid column weights
        for col in range(columns):
            self.scrollable_frame.grid_columnconfigure(col, weight=1)
    
    def select_image(self, image_path, button):
        """Load and display selected image."""
        print(f"Image selected: {image_path}")
        
        # Highlight current button (keep previous ones green too)
        button.configure(bg="#00AA00")  # Green color for selected
        self.selected_buttons.add(button)
        
        self.current_image_path = image_path
        self.display_image_preview(image_path)
    
    def display_image_preview(self, image_path):
        """Display the selected image in the canvas."""
        try:
            # Load the image
            self.original_image = Image.open(image_path)
            
            # Scale image to fit canvas while maintaining aspect ratio
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
            
            # Display image info
            info_text = f"File: {os.path.basename(image_path)} | Size: {self.original_image.width}x{self.original_image.height}"
            self.canvas.create_text(canvas_width//2, 20, text=info_text, 
                                  fill="black", font=("Arial", 10), 
                                  anchor="center")
            
        except Exception as e:
            print(f"Error loading image: {e}")
            messagebox.showerror("Error", f"Could not load image: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageBrowser(root)
    root.mainloop()
