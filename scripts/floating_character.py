#!/usr/bin/env python3
"""
Floating Character Window
A draggable, always-on-top window displaying the character image.
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys

class FloatingCharacter:
    """A draggable floating window with character image"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Fishing Game Character")
        
        # Make window always on top
        self.root.wm_attributes("-topmost", True)
        
        # Remove window decorations (title bar, etc.) for a cleaner look
        self.root.overrideredirect(True)
        
        # Variables for dragging
        self.drag_data = {"x": 0, "y": 0}
        
        # Load and display character image
        self.setup_image()
        
        # Setup dragging
        self.setup_dragging()
        
        # Add right-click menu
        self.setup_menu()
        
        # Position window
        self.center_window()
        
        # Make window semi-transparent (optional)
        self.root.wm_attributes("-alpha", 0.9)
    
    def setup_image(self):
        """Load and display the character image"""
        try:
            # Get the path to the image - try multiple possible locations
            base_path = os.path.dirname(os.path.dirname(__file__))
            
            # Try different image paths in order of preference
            possible_paths = [
                os.path.join(base_path, "images", "idle_character.png"),           # Main character
                os.path.join(base_path, "images", "base_models", "character.png"), # Fallback in base_models
                os.path.join(base_path, "images", "character.png")                 # Legacy fallback
            ]
            
            image_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    image_path = path
                    break
            
            if image_path is None:
                raise FileNotFoundError(f"Character image not found in any of the expected locations: {possible_paths}")
            
            # Load image with PIL
            pil_image = Image.open(image_path)
            
            # Resize image if it's too large (max 200x200)
            max_size = 200
            pil_image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            self.photo = ImageTk.PhotoImage(pil_image)
            
            # Create label with image
            self.image_label = tk.Label(
                self.root, 
                image=self.photo,
                bg="white",
                relief="solid",
                borderwidth=2
            )
            self.image_label.pack(padx=5, pady=5)
            
            # Add character name/title
            self.title_label = tk.Label(
                self.root,
                text="🎣 Fishing Character",
                bg="white",
                font=("Arial", 10, "bold"),
                relief="solid",
                borderwidth=1
            )
            self.title_label.pack(fill="x", padx=5, pady=(0, 5))
            
            print(f"✅ Character image loaded: {image_path}")
            
        except Exception as e:
            print(f"❌ Error loading character image: {e}")
            # Create a fallback label
            self.image_label = tk.Label(
                self.root,
                text="🎣\nFishing\nCharacter\n(Image not found)",
                bg="lightblue",
                font=("Arial", 12),
                width=15,
                height=8,
                relief="solid",
                borderwidth=2
            )
            self.image_label.pack(padx=5, pady=5)
    
    def setup_dragging(self):
        """Setup mouse dragging functionality"""
        # Bind drag events to both the image and title
        for widget in [self.image_label, self.title_label]:
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.on_drag)
            widget.bind("<ButtonRelease-1>", self.stop_drag)
    
    def start_drag(self, event):
        """Start dragging the window"""
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def on_drag(self, event):
        """Handle window dragging with screen boundary constraints"""
        # Calculate new position
        new_x = self.root.winfo_x() + (event.x - self.drag_data["x"])
        new_y = self.root.winfo_y() + (event.y - self.drag_data["y"])
        
        # Get screen and window dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Constrain to screen boundaries
        new_x = max(0, min(new_x, screen_width - window_width))
        new_y = max(0, min(new_y, screen_height - window_height))
        
        # Move window
        self.root.geometry(f"+{new_x}+{new_y}")
    
    def stop_drag(self, event):
        """Stop dragging"""
        pass
    
    def setup_menu(self):
        """Setup right-click context menu"""
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="📌 Always on Top", command=self.toggle_topmost)
        self.menu.add_command(label="👻 Toggle Transparency", command=self.toggle_transparency)
        self.menu.add_separator()
        self.menu.add_command(label="🏠 Center Window", command=self.center_window)
        self.menu.add_separator()
        self.menu.add_command(label="❌ Close", command=self.close_window)
        
        # Bind right-click to show menu
        for widget in [self.image_label, self.title_label]:
            widget.bind("<Button-3>", self.show_menu)
    
    def show_menu(self, event):
        """Show context menu"""
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()
    
    def toggle_topmost(self):
        """Toggle always on top"""
        current = self.root.wm_attributes("-topmost")
        self.root.wm_attributes("-topmost", not current)
        status = "ON" if not current else "OFF"
        print(f"Always on top: {status}")
    
    def toggle_transparency(self):
        """Toggle between opaque and semi-transparent"""
        current_alpha = self.root.wm_attributes("-alpha")
        new_alpha = 0.9 if current_alpha == 1.0 else 1.0
        self.root.wm_attributes("-alpha", new_alpha)
        status = "Semi-transparent" if new_alpha == 0.9 else "Opaque"
        print(f"Window transparency: {status}")
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        
        # Get window size
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Get screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate center position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"+{x}+{y}")
        print("Window centered")
    
    def close_window(self):
        """Close the window"""
        print("Closing floating character window...")
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Start the floating window"""
        print("🎣 Starting floating character window...")
        print("💡 Right-click for options menu")
        print("💡 Left-click and drag to move window")
        print("💡 Press Ctrl+C in terminal to close")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nClosing floating character window...")
            self.root.quit()

# Standalone launcher
class FloatingCharacterLauncher:
    """Simple launcher with options"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Floating Character Launcher")
        self.root.geometry("300x200")
        self.root.resizable(False, False)
        
        # Center the launcher
        self.center_window()
        
        self.setup_ui()
    
    def center_window(self):
        """Center launcher window"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 300) // 2
        y = (self.root.winfo_screenheight() - 200) // 2
        self.root.geometry(f"300x200+{x}+{y}")
    
    def setup_ui(self):
        """Setup launcher UI"""
        # Title
        title = tk.Label(
            self.root,
            text="🎣 Fishing Character",
            font=("Arial", 16, "bold"),
            pady=20
        )
        title.pack()
        
        # Description
        desc = tk.Label(
            self.root,
            text="Launch a floating, draggable character window\nthat stays always on top",
            justify="center",
            pady=10
        )
        desc.pack()
        
        # Buttons frame
        buttons_frame = tk.Frame(self.root)
        buttons_frame.pack(pady=20)
        
        # Launch button
        launch_btn = tk.Button(
            buttons_frame,
            text="🚀 Launch Floating Character",
            command=self.launch_character,
            bg="lightgreen",
            font=("Arial", 12),
            padx=20,
            pady=10
        )
        launch_btn.pack(pady=5)
        
        # Exit button
        exit_btn = tk.Button(
            buttons_frame,
            text="❌ Exit",
            command=self.root.quit,
            bg="lightcoral",
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        exit_btn.pack(pady=5)
    
    def launch_character(self):
        """Launch the floating character window"""
        self.root.withdraw()  # Hide launcher
        
        try:
            character = FloatingCharacter()
            character.run()
        except Exception as e:
            print(f"Error launching character window: {e}")
        finally:
            self.root.quit()
    
    def run(self):
        """Run the launcher"""
        self.root.mainloop()

# Main execution
if __name__ == "__main__":
    # Check if PIL is available
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("❌ PIL (Pillow) is required for image display")
        print("Install it with: pip install Pillow")
        sys.exit(1)
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--direct":
        # Launch character window directly
        character = FloatingCharacter()
        character.run()
    else:
        # Show launcher first
        launcher = FloatingCharacterLauncher()
        launcher.run()
