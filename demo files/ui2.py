import tkinter as tk
import uiautomation as auto
import threading
import time
import ctypes
from pynput import keyboard

TRANS_COLOR = "#ff00ff"

class SmartOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.visible = False
        self.running = True
        self.cursor_x = 0
        self.cursor_y = 0
        self.suggestions = ["", "", ""]
        self.on_select_callback = None
        
        # Setup window
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg=TRANS_COLOR)
        self.root.attributes("-transparentcolor", TRANS_COLOR)
        self.root.withdraw()
        
        # Create frame
        self.frame = tk.Frame(self.root, bg=TRANS_COLOR)
        self.frame.pack()
        
        # Create 3 suggestion labels with background
        self.labels = []
        
        # Create a main container with black background
        self.bg_container = tk.Frame(self.frame, bg="#202020", highlightthickness=0)
        self.bg_container.pack(fill="both", expand=True)
        
        for i in range(3):
            label = tk.Label(
                self.bg_container,
                text="",
                font=("Segoe UI", 11, "bold"),
                bg="#202020",
                fg="white",
                anchor="w",
                padx=10,
                pady=4
            )
            self.labels.append(label)
        
        # Apply click-through
        self.root.after(100, self._apply_click_through)
        
        # Start tracking cursor
        threading.Thread(target=self._track_cursor, daemon=True).start()
        
        # Setup keyboard listener
        self._setup_keyboard_listener()
        
        # Start position update loop
        self._update_position()
    
    def _apply_click_through(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            LWA_COLORKEY = 0x00000001
            LWA_ALPHA = 0x00000002
            
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = style | WS_EX_LAYERED | WS_EX_TRANSPARENT
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            
            # Set the background to 70% opacity (179 out of 255)
            ctypes.windll.user32.SetLayeredWindowAttributes(
                hwnd, 
                int(TRANS_COLOR.replace('#', ''), 16),
                179,
                LWA_COLORKEY | LWA_ALPHA
            )
        except:
            pass
    
    def _track_cursor(self):
        while self.running:
            try:
                element = auto.GetFocusedControl()
                if element:
                    pattern = element.GetPattern(auto.PatternId.TextPattern)
                    if pattern:
                        selection = pattern.GetSelection()
                        if selection:
                            rect = selection[0].GetBoundingRectangles()[0]
                            self.cursor_x = rect.left + 15
                            self.cursor_y = rect.bottom + 10
            except:
                pass
            time.sleep(0.05)
    
    def _setup_keyboard_listener(self):
        self.alt_pressed = False
        
        def on_press(key):
            # Track Alt key state
            if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                self.alt_pressed = True
                return
            
            if not self.visible or not self.alt_pressed:
                return
            
            try:
                if hasattr(key, 'char') and key.char:
                    char = key.char.lower()
                    if char == 'b':
                        self._select_suggestion(0)
                    elif char == 'n':
                        self._select_suggestion(1)
                    elif char == 'm':
                        self._select_suggestion(2)
            except:
                pass
        
        def on_release(key):
            if key in (keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r):
                self.alt_pressed = False
        
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
    
    def _select_suggestion(self, index):
        if 0 <= index < 3 and self.suggestions[index]:
            if self.on_select_callback:
                self.on_select_callback(index, self.suggestions[index])
    
    def _update_position(self):
        if self.visible and self.cursor_x > 0 and self.cursor_y > 0:
            self.root.geometry(f"+{self.cursor_x}+{self.cursor_y}")
        self.root.after(16, self._update_position)
    
    def set_suggestions(self, suggestion1="", suggestion2="", suggestion3=""):
        """Set the 3 suggestions"""
        self.suggestions = [suggestion1, suggestion2, suggestion3]
        self.root.after(0, self._update_labels)
    
    def _update_labels(self):
        shortcuts = ["Alt+B", "Alt+N", "Alt+M"]
        has_content = False
        
        for i, (text, shortcut) in enumerate(zip(self.suggestions, shortcuts)):
            label = self.labels[i]
            if text:
                display_text = f"{text}  ({shortcut})"
                label.config(text=display_text)
                label.pack(fill="x")
                has_content = True
            else:
                label.pack_forget()
        
        if has_content:
            self.visible = True
            self.root.deiconify()
        else:
            self.hide()
    
    def show(self):
        """Show the overlay"""
        self.root.after(0, self._show)
    
    def _show(self):
        self.visible = True
        self.root.deiconify()
    
    def hide(self):
        """Hide the overlay"""
        self.root.after(0, self._hide)
    
    def _hide(self):
        self.visible = False
        self.root.withdraw()
    
    def is_visible(self):
        """Check if overlay is visible"""
        return self.visible
    
    def on_select(self, callback):
        """Set callback for when user selects a suggestion
        callback(index, text) will be called"""
        self.on_select_callback = callback
    
    def run(self):
        """Start the main loop"""
        self.root.mainloop()
    
    def stop(self):
        """Stop the overlay"""
        self.running = False
        self.root.quit()


# --- DEMO ---
if __name__ == "__main__":
    overlay = SmartOverlay()
    
    # Set callback for when user selects
    def on_suggestion_selected(index, text):
        print(f"Selected suggestion {index + 1}: {text}")
        overlay.hide()
        time.sleep(1)
        overlay.set_suggestions("New 1", "New 2", "New 3")
    
    overlay.on_select(on_suggestion_selected)
    
    def demo():
        time.sleep(1)
        
        # Show 3 suggestions
        overlay.set_suggestions(
            "import numpy as np",
            "import pandas as pd", 
            "import matplotlib.pyplot as plt"
        )
        time.sleep(3)
        
        # Update to different suggestions
        overlay.set_suggestions(
            "def function():",
            "class MyClass:",
            "if __name__ == '__main__':"
        )
        time.sleep(3)
        
        # Show only 2 suggestions
        overlay.set_suggestions(
            "First option",
            "Second option"
        )
        time.sleep(3)
        
        # Hide
        overlay.hide()
    
    threading.Thread(target=demo, daemon=True).start()
    overlay.run()