#!/usr/bin/env python3
"""
Simple Floating Character Window
A lightweight draggable window displaying the character image.
"""

import tkinter as tk
from PIL import Image, ImageTk
import os
import asyncio
import websockets
import json
import threading
import time

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
        
        # Fishing excitement state
        self.showing_excitement = False
        self.original_image = None
        self.caught_image = None
        
        self.setup_window()
        self.setup_dragging()
        self.position_window()
        
        # Setup periodic excitement for testing
        self.setup_periodic_excitement()
    
    def setup_window(self):
        """Setup the window with character image"""
        try:
            # Load both character images (from parent directory)
            base_path = os.path.dirname(os.path.dirname(__file__))
            normal_image_path = os.path.join(base_path, "images", "idle_character.png")
            caught_image_path = os.path.join(base_path, "images", "caught_character.png")
            
            if os.path.exists(normal_image_path):
                # Load and process normal character image
                self.original_image = self.load_and_process_image(normal_image_path)
                
                # Load and process caught character image
                if os.path.exists(caught_image_path):
                    self.caught_image = self.load_and_process_image(caught_image_path)
                    print(f"✅ Both character images loaded successfully")
                else:
                    print(f"⚠️ Caught character image not found at: {caught_image_path}")
                    self.caught_image = self.original_image  # Use same image as fallback
                
                # Create image label with normal character image
                self.label = tk.Label(
                    self.root,
                    image=self.original_image,
                    bg="gray90",  # Light gray background that will be made transparent
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
                    bg="gray90",  # This will be made transparent
                    width=4,
                    height=2,
                    relief="flat",
                    borderwidth=0,
                    cursor="hand2"
                )
            
            self.label.pack()
            
            # Make the background transparent (using gray90 as transparent color)
            self.root.configure(bg='gray90')
            self.root.wm_attributes('-transparentcolor', 'gray90')
            
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
        """Handle dragging with screen boundary constraints"""
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
        
        self.root.geometry(f"+{new_x}+{new_y}")
    
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
        """Position window in top-right corner with screen boundary checks"""
        self.root.update_idletasks()
        
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Position in top-right corner with some margin
        x = screen_width - window_width - 20
        y = 20
        
        # Ensure window stays within screen boundaries
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))
        
        self.root.geometry(f"+{x}+{y}")
    
    def setup_periodic_excitement(self):
        """Setup periodic excitement animation and fish signal monitoring"""
        # Check for fish caught signals every 100ms
        self.check_for_fish_signal()
        
    def trigger_periodic_excitement(self):
        """Trigger excitement and schedule next one"""  
        self.show_excitement()
        
        # Schedule next excitement
        import random
        next_excitement = random.randint(10000, 30000)  # 10-30 seconds
        self.root.after(next_excitement, self.trigger_periodic_excitement)
    
    def listen_for_fish_catches(self):
        """Listen for fish catch events from the game server"""
        async def connect_and_listen():
            try:
                # Try to connect to the game server
                websocket = await websockets.connect("ws://localhost:8765")
                
                # Send a simple join request as observer
                join_message = {
                    "type": "join_lobby",
                    "lobby_code": "OBSERVER",  # This won't work but we'll try anyway
                    "player_name": "FloatingCharacter"
                }
                await websocket.send(json.dumps(join_message))
                
                # Listen for messages
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if data.get("type") == "fish_caught":
                            # Show excitement when any player catches a fish
                            self.root.after(0, self.show_excitement)
                    except:
                        pass
                        
            except Exception as e:
                print(f"Character connection to game server failed: {e}")
        
        try:
            asyncio.run(connect_and_listen())
        except:
            pass
    
    def check_for_fish_signal(self):
        """Check for fish caught signal file and trigger excitement"""
        try:
            # Signal file is in parent directory
            signal_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fish_caught_signal.tmp")
            if os.path.exists(signal_file):
                # Read the timestamp
                with open(signal_file, "r") as f:
                    timestamp = float(f.read().strip())
                
                # Check if this signal is new (within last 5 seconds)
                if time.time() - timestamp < 5:
                    self.show_excitement()
                    
                # Remove the signal file
                os.remove(signal_file)
                
        except Exception as e:
            pass  # Ignore any errors in signal checking
        
        # Schedule next check in 100ms
        self.root.after(100, self.check_for_fish_signal)

    def show_excitement(self):
        """Show excitement by changing to caught character image"""
        if self.showing_excitement or not self.caught_image:
            return
        
        self.showing_excitement = True
        
        # Change to caught character image
        self.label.configure(image=self.caught_image)
        print("🐟 Fish caught! Character image changed to caught_character.png")
        
        # Revert back to normal image after 2 seconds
        self.root.after(2000, self.hide_excitement)
    
    def hide_excitement(self):
        """Revert back to normal character image"""
        if self.original_image:
            self.label.configure(image=self.original_image)
        self.showing_excitement = False
        print("Character reverted to normal image")
    
    def close(self):
        """Close the window"""
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the floating character"""
        print("🎣 Floating character launched!")
        print("💡 Left-click and drag to move (constrained to screen)")
        print("💡 Right-click to toggle always-on-top")
        print("💡 Double-click to close")
        print("💡 Background is transparent - only character shows!")
        print("🐟 Character will change to caught_character.png when fish are caught!")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.close()
    
    def load_and_process_image(self, image_path):
        """Load and process an image with transparency support"""
        # Load and resize image
        pil_image = Image.open(image_path)
        pil_image.thumbnail((150, 150), Image.Resampling.LANCZOS)
        
        # Convert to RGBA for transparency support
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')
        
        # Create a transparent background version
        # This preserves white pixels in the character while making background transparent
        data = pil_image.getdata()
        new_data = []
        for item in data:
            # Only make pure white pixels (255,255,255) at edges transparent
            # This is a simple approach - you might want to refine this
            if item[:3] == (255, 255, 255) and len(item) == 4:
                # Keep white pixels but with slight opacity to distinguish from pure background
                new_data.append((255, 255, 255, 200))  # Slightly transparent white
            else:
                new_data.append(item)
        
        pil_image.putdata(new_data)
        return ImageTk.PhotoImage(pil_image)

if __name__ == "__main__":
    app = SimpleFloatingCharacter()
    app.run()
