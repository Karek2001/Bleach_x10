#!/usr/bin/env python3
"""Pixel Picker GUI

Small utility to display an image, let you zoom with the mouse‑wheel, and copy the
clicked pixel's coordinates and colour (hex) to the clipboard in the format
"x,y","#rrggbb".

Dependencies (install with pip):
    pillow pyperclip

Usage:
    python pixel_picker.py
Press Ctrl+O to choose an image.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pyperclip


class PixelPicker:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Pixel Picker – click to copy colour & position")

        # Create frame for canvas and scrollbars
        canvas_frame = tk.Frame(root)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas where the image is drawn
        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0, cursor="cross")
        
        # Scrollbars
        v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        h_scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Status bar at the bottom
        self.status = tk.Label(root, text="Ctrl+O: open | Click: set zoom center | Ctrl+/- : zoom | Ctrl+arrows: pan", anchor="w")
        self.status.pack(fill=tk.X)

        # State
        self.original: Image.Image | None = None  # the source image (RGB)
        self.zoom = 1.0  # current zoom factor
        self.photo: ImageTk.PhotoImage | None = None  # Tk photo for display
        self.zoom_center_x = None  # x coordinate for zoom center
        self.zoom_center_y = None  # y coordinate for zoom center

        # Bindings
        root.bind("<Control-o>", self.open_image)
        root.bind("<Control-plus>", self.on_zoom_in)     # Ctrl + "+" to zoom in
        root.bind("<Control-minus>", self.on_zoom_out)   # Ctrl + "-" to zoom out
        root.bind("<Control-equal>", self.on_zoom_in)    # Ctrl + "=" (same as + without shift)
        root.bind("<Control-Left>", self.on_pan_left)    # Ctrl + Left to pan left
        root.bind("<Control-Right>", self.on_pan_right)  # Ctrl + Right to pan right
        root.bind("<Control-Up>", self.on_pan_up)        # Ctrl + Up to pan up
        root.bind("<Control-Down>", self.on_pan_down)    # Ctrl + Down to pan down
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)  # Track mouse position

    # ──────────────────────────────────────────────────────────────────────────
    # File handling & rendering
    # ──────────────────────────────────────────────────────────────────────────
    def open_image(self, _event=None) -> None:
        """Open an image via file‑dialog and reset zoom."""
        path = filedialog.askopenfilename(
            title="Select image",
            initialdir="/mnt/hetzner-storage-sub1",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        try:
            self.original = Image.open(path).convert("RGB")
        except Exception as err:
            messagebox.showerror("Error", f"Cannot open image:\n{err}")
            return

        self.zoom = 1.0
        self._refresh()

    def _refresh(self) -> None:
        """Redraw the image at the current zoom level."""
        if self.original is None:
            return

        w, h = self.original.size
        new_w, new_h = int(w * self.zoom), int(h * self.zoom)

        # Resize using nearest neighbour so individual pixels stay crisp
        resized = self.original.resize((new_w, new_h), Image.NEAREST)
        self.photo = ImageTk.PhotoImage(resized)

        self.canvas.configure(width=new_w, height=new_h, scrollregion=(0, 0, new_w, new_h))
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.status.config(text=f"Zoom: {self.zoom:.2f}×  |  Image: {w}×{h}")

    # ──────────────────────────────────────────────────────────────────────────
    # Interaction
    # ──────────────────────────────────────────────────────────────────────────
    def on_mouse_move(self, event) -> None:
        """Track mouse position for zoom centering."""
        # Set zoom center to current mouse position
        self.zoom_center_x = event.x
        self.zoom_center_y = event.y

    def on_zoom_in(self, _event=None) -> None:
        """Zoom in using Ctrl + plus."""
        if self.original is None:
            return
        self._apply_zoom(1.2)

    def on_zoom_out(self, _event=None) -> None:
        """Zoom out using Ctrl + minus."""
        if self.original is None:
            return
        self._apply_zoom(0.8)

    def on_pan_left(self, _event=None) -> None:
        """Pan left using Ctrl + Left arrow."""
        self._pan(-50, 0)

    def on_pan_right(self, _event=None) -> None:
        """Pan right using Ctrl + Right arrow."""
        self._pan(50, 0)

    def on_pan_up(self, _event=None) -> None:
        """Pan up using Ctrl + Up arrow."""
        self._pan(0, -50)

    def on_pan_down(self, _event=None) -> None:
        """Pan down using Ctrl + Down arrow."""
        self._pan(0, 50)

    def _pan(self, dx: int, dy: int) -> None:
        """Pan the image by dx, dy pixels."""
        if self.original is None:
            return
            
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        image_width = int(self.original.width * self.zoom)
        image_height = int(self.original.height * self.zoom)
        
        # Get current scroll position
        current_x = self.canvas.canvasx(0)
        current_y = self.canvas.canvasy(0)
        
        # Calculate new scroll position
        new_x = current_x + dx
        new_y = current_y + dy
        
        # Apply horizontal pan
        if image_width > canvas_width:
            max_scroll_x = image_width - canvas_width
            frac_x = max(0, min(1, new_x / max_scroll_x)) if max_scroll_x > 0 else 0
            self.canvas.xview_moveto(frac_x)
            
        # Apply vertical pan
        if image_height > canvas_height:
            max_scroll_y = image_height - canvas_height
            frac_y = max(0, min(1, new_y / max_scroll_y)) if max_scroll_y > 0 else 0
            self.canvas.yview_moveto(frac_y)
        
        # Update zoom center to current canvas center after panning
        self.zoom_center_x = canvas_width / 2
        self.zoom_center_y = canvas_height / 2

    def _apply_zoom(self, factor: float) -> None:
        """Apply zoom with the given factor, centered on the zoom center point."""
        new_zoom = self.zoom * factor
        if 0.1 < new_zoom < 20:  # sane limits
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Use zoom center if set, otherwise use canvas center
            if self.zoom_center_x is not None and self.zoom_center_y is not None:
                center_x = self.zoom_center_x
                center_y = self.zoom_center_y
            else:
                center_x = canvas_width / 2
                center_y = canvas_height / 2
            
            # Get current scroll position and calculate image coordinates
            scroll_x = self.canvas.canvasx(0)
            scroll_y = self.canvas.canvasy(0)
            
            # Find image pixel coordinates under the center point
            image_pixel_x = (scroll_x + center_x) / self.zoom
            image_pixel_y = (scroll_y + center_y) / self.zoom
            
            # Apply zoom
            self.zoom = new_zoom
            self._refresh()
            
            # Calculate new scroll to keep the pixel at the center point
            new_scroll_x = (image_pixel_x * self.zoom) - center_x
            new_scroll_y = (image_pixel_y * self.zoom) - center_y
            
            # Apply scroll
            new_width = int(self.original.width * self.zoom)
            new_height = int(self.original.height * self.zoom)
            
            if new_width > canvas_width:
                max_x = new_width - canvas_width
                frac_x = max(0, min(1, new_scroll_x / max_x)) if max_x > 0 else 0
                self.canvas.xview_moveto(frac_x)
                
            if new_height > canvas_height:
                max_y = new_height - canvas_height  
                frac_y = max(0, min(1, new_scroll_y / max_y)) if max_y > 0 else 0
                self.canvas.yview_moveto(frac_y)

    def on_click(self, event) -> None:
        if self.original is None:
            return
        
        # Set zoom center to clicked position
        self.zoom_center_x = event.x
        self.zoom_center_y = event.y

        # Get scroll position and calculate image coordinates
        scroll_x = self.canvas.canvasx(0)
        scroll_y = self.canvas.canvasy(0)
        
        # Translate canvas coordinates back to original image
        x = int((scroll_x + event.x) / self.zoom)
        y = int((scroll_y + event.y) / self.zoom)
        if not (0 <= x < self.original.width and 0 <= y < self.original.height):
            return

        r, g, b = self.original.getpixel((x, y))
        hex_colour = f"#{r:02x}{g:02x}{b:02x}"
        payload = f'"{x},{y}","{hex_colour}"'
        pyperclip.copy(payload)
        self.status.config(text=f"Copied → {payload} (Zoom center set)")


# ─────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    root = tk.Tk()
    picker = PixelPicker(root)
    # Start with a comfortable window size
    root.geometry("600x900")
    root.mainloop()


if __name__ == "__main__":
    main()
