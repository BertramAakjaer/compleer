import tkinter as tk # We use standard tkinter for the root window
import uiautomation as auto
import threading
import time
import ctypes

# --- Configuration ---
# We use Fuchsia (Magenta) as the transparency key. 
# It's a standard color for this because it rarely appears in UI.
TRANS_COLOR = "#ff00ff" 

class CursorTracker:
    """Background worker that finds the text cursor."""
    def __init__(self):
        self.x = 0
        self.y = 0
        self.running = True
        self._start_thread()

    def _start_thread(self):
        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    def _loop(self):
        while self.running:
            try:
                element = auto.GetFocusedControl()
                if element:
                    pattern = element.GetPattern(auto.PatternId.TextPattern)
                    if pattern:
                        selection = pattern.GetSelection()
                        if selection:
                            rect = selection[0].GetBoundingRectangles()[0]
                            self.x, self.y = rect.left, rect.bottom
            except Exception:
                pass
            time.sleep(0.03)

    def get_position(self):
        return self.x, self.y

class WindowUtils:
    @staticmethod
    def set_click_through(hwnd):
        """Forces the window to be click-through and layered."""
        try:
            # Get current styles
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            
            # Add Layered (required for transparency) and Transparent (click-through)
            style = style | WS_EX_LAYERED | WS_EX_TRANSPARENT
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
        except Exception as e:
            print(f"Error setting window style: {e}")

class OverlayApp:
    def __init__(self):
        # 1. Use standard Tkinter (Not CustomTkinter) for the root
        self.root = tk.Tk()
        
        # 2. Configure the window to be a "Green Screen"
        self.root.overrideredirect(True)      # Remove title bar
        self.root.attributes("-topmost", True)# Always on top
        self.root.config(bg=TRANS_COLOR)      # Set background to key color
        
        # This command tells Windows: "Make this specific color invisible"
        self.root.attributes("-transparentcolor", TRANS_COLOR)
        
        # 3. Create the Dot
        # We use a Canvas for a perfect circle (better than a text label)
        self.canvas = tk.Canvas(self.root, width=40, height=40, 
                                bg=TRANS_COLOR, highlightthickness=0)
        self.canvas.pack()
        
        # Draw the dot (x1, y1, x2, y2)
        # Change 'cyan' to whatever color you want the dot to be
        self.dot = self.canvas.create_oval(10, 10, 25, 25, fill="#00FF99", outline="")

        # 4. Logic Setup
        self.tracker = CursorTracker()
        self.current_x = 0.0
        self.current_y = 0.0
        
        # Move offscreen initially
        self.root.geometry("40x40+-100+-100")

        # 5. Apply Click-Through (Delayed to ensure window is ready)
        self.root.after(100, self.apply_hacks)

        # 6. Start Loop
        self.animate()
        self.root.mainloop()

    def apply_hacks(self):
        # We need the HWND (Window ID) to talk to the Windows API
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        WindowUtils.set_click_through(hwnd)

    def animate(self):
        target_x, target_y = self.tracker.get_position()
        
        # Linear Interpolation (Lerp) for smoothing
        dx = target_x - self.current_x
        dy = target_y - self.current_y

        if abs(dx) > 1 or abs(dy) > 1:
            self.current_x += dx * 0.25
            self.current_y += dy * 0.25
            
            # Offset calculation:
            # We subtract 20 from X to center the 40px wide window
            # We add 5 to Y to push it below the text line
            final_x = int(self.current_x) - 10
            final_y = int(self.current_y) + 5
            
            self.root.geometry(f"40x40+{final_x}+{final_y}")

        self.root.after(16, self.animate)

if __name__ == "__main__":
    OverlayApp()