#!/usr/bin/env python3
"""
Simple Floating Character Window
A lightweight draggable window displaying the character image.
"""

import tkinter as tk
from PIL import Image, ImageTk
import os

class SimpleFloatingCharacter:
    """A simple draggable floating character window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎣 Fishing Character")
        
        # Make window always on top and frameless
        self.root.wm_attributes("-topmost", True)
        self.root.overrideredirect(True)
        
        # Variables for dragging
        self.drag_data = {"x": 0, "y": 0}
        
        self.setup_window()
        self.setup_dragging()
        self.position_window()
    
    def setup_window(self):
        """Setup the window with character image"""
        try:
            # Load character image
            image_path = os.path.join(os.path.dirname(__file__), "images", "character.png")
            
            if os.path.exists(image_path):
                # Load and resize image
                pil_image = Image.open(image_path)
                pil_image.thumbnail((150, 150), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(pil_image)
                
                # Create image label with transparent background
                self.label = tk.Label(
                    self.root,
                    image=self.photo,
                    bg="white",  # This will be made transparent
                    relief="flat",
                    borderwidth=0,
                    cursor="hand2"
                )
            else:
                # Fallback if image not found
                self.label = tk.Label(
                    self.root,
                    text="🎣",
                    font=("Arial", 48),
                    bg="white",  # This will be made transparent
                    width=4,
                    height=2,
                    relief="flat",
                    borderwidth=0,
                    cursor="hand2"
                )
            
            self.label.pack()
            
            # Make the background transparent
            self.root.configure(bg='white')
            self.root.wm_attributes('-transparentcolor', 'white')
            
        except Exception as e:
            print(f"Error setting up window: {e}")
            self.close()
    
    def setup_dragging(self):
        """Setup dragging functionality"""
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.on_drag)
        self.label.bind("<ButtonRelease-1>", self.stop_drag)
        
        # Right-click to toggle always on top
        self.label.bind("<Button-3>", self.toggle_topmost)
        
        # Double-click to close (since no X button)
        self.label.bind("<Double-Button-1>", self.double_click_close)
    
    def start_drag(self, event):
        """Start dragging"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def on_drag(self, event):
        """Handle dragging"""
        x = self.root.winfo_x() + (event.x - self.drag_data["x"])
        y = self.root.winfo_y() + (event.y - self.drag_data["y"])
        self.root.geometry(f"+{x}+{y}")
    
    def stop_drag(self, event):
        """Stop dragging"""
        pass
    
    def toggle_topmost(self, event):
        """Toggle always on top with right-click"""
        current = self.root.wm_attributes("-topmost")
        self.root.wm_attributes("-topmost", not current)
        print(f"Always on top: {'OFF' if current else 'ON'}")
    
    def double_click_close(self, event):
        """Close window on double-click"""
        self.close()
    
    def position_window(self):
        """Position window in top-right corner"""
        self.root.update_idletasks()
        
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        
        # Position in top-right corner with some margin
        x = screen_width - window_width - 20
        y = 20
        
        self.root.geometry(f"+{x}+{y}")
    
    def close(self):
        """Close the window"""
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the floating character"""
        print("🎣 Floating character launched!")
        print("💡 Left-click and drag to move")
        print("💡 Right-click to toggle always-on-top")
        print("💡 Double-click to close")
        print("💡 Background is transparent - only character shows!")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.close()

if __name__ == "__main__":
    app = SimpleFloatingCharacter()
    app.run()
