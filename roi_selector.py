import cv2
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import os
import subprocess
import platform

# --- Global Variables for OpenCV ---
ref_point = []
cropping = False
image_for_cv = None
clone = None

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


def click_and_crop(event, x, y, flags, param):
    """Mouse callback function to handle drawing the rectangle in the OpenCV window."""
    global ref_point, cropping, image_for_cv, clone

    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]
        cropping = True
    elif event == cv2.EVENT_LBUTTONUP:
        ref_point.append((x, y))
        cropping = False

        cv2.rectangle(image_for_cv, ref_point[0], ref_point[1], (0, 255, 0), 2)
        cv2.imshow("ROI Selector", image_for_cv)

        x_start, y_start = ref_point[0]
        x_end, y_end = ref_point[1]
        
        x_coord = min(x_start, x_end)
        y_coord = min(y_start, y_end)
        width = abs(x_start - x_end)
        height = abs(y_start - y_end)

        roi_string = f'"roi": [{x_coord}, {y_coord}, {width}, {height}]'
        
        print("\n--- ROI Coordinates ---")
        print(f"Copy this into your config.json:")
        print(roi_string)
        print("-----------------------")
        copy_to_clipboard(roi_string)


def launch_roi_editor(image_path):
    """Launches the OpenCV window for a selected image."""
    global image_for_cv, clone
    
    image_for_cv = cv2.imread(image_path)
    if image_for_cv is None:
        print(f"Error: Could not load image from path: {image_path}")
        return
        
    clone = image_for_cv.copy()
    cv2.namedWindow("ROI Selector")
    cv2.setMouseCallback("ROI Selector", click_and_crop)

    print("\n--- ROI Selector Launched ---")
    print("1. Click and drag your mouse on the image to draw a rectangle.")
    print("2. Release the mouse to get the ROI coordinates.")
    print("3. Press 'r' to reset the selection.")
    print("4. Press 'q' to quit the ROI selector.")

    while True:
        cv2.imshow("ROI Selector", image_for_cv)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("r"):
            image_for_cv = clone.copy()
            print("\nSelection reset.")
        elif key == ord("q"):
            break
            
    cv2.destroyAllWindows()


class ImageSelectorApp:
    """The main GUI application to browse and select an image."""
    def __init__(self, root, image_dir):
        self.root = root
        self.image_dir = image_dir
        self.root.title("Screenshot Selector")
        self.root.geometry("800x600")

        # --- Styling ---
        self.root.configure(bg="#2E2E2E")
        self.header_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.list_font = font.Font(family="Helvetica", size=10)
        
        # --- Layout ---
        header_label = tk.Label(self.root, text="Select a Screenshot to Analyze", font=self.header_font, bg="#2E2E2E", fg="#FFFFFF", pady=10)
        header_label.pack()

        # --- Canvas and Scrollbar for the list ---
        canvas = tk.Canvas(self.root, bg="#3C3C3C", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#3C3C3C")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        self.populate_images(scrollable_frame)

    def populate_images(self, frame):
        """Scans the directory and populates the GUI with image files."""
        try:
            image_files = [f for f in os.listdir(self.image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        except FileNotFoundError:
            label = tk.Label(frame, text=f"Error: Directory not found:\n{self.image_dir}", font=self.list_font, bg="#3C3C3C", fg="#FF5555", padx=10, pady=10)
            label.pack()
            return

        if not image_files:
            label = tk.Label(frame, text="No images found in the directory.", font=self.list_font, bg="#3C3C3C", fg="#FFFFFF", padx=10, pady=10)
            label.pack()
            return

        for filename in sorted(image_files, reverse=True): # Show newest first
            path = os.path.join(self.image_dir, filename)
            
            # Create a button for each image
            btn = tk.Button(frame, text=filename, font=self.list_font,
                            command=lambda p=path: self.select_image(p),
                            bg="#555555", fg="#FFFFFF", relief="flat", padx=10, pady=5, anchor="w")
            btn.pack(fill="x", padx=5, pady=2)

    def select_image(self, image_path):
        """Callback for when an image button is clicked."""
        print(f"\nImage selected: {image_path}")
        self.root.destroy()  # Close the selector GUI
        launch_roi_editor(image_path) # Launch the OpenCV window


if __name__ == "__main__":
    # Define the default directory for screenshots
    default_directory = "/home/karek/Downloads/shared/"

    # Create and run the main GUI application
    main_root = tk.Tk()
    app = ImageSelectorApp(main_root, default_directory)
    main_root.mainloop()

    print("\nGUI closed. Application finished.")