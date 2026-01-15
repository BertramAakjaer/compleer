import customtkinter as ctk
import threading
import queue
import time
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class UIDisplayer:
    _msg_queue: queue.Queue = field(default_factory=queue.Queue)
    
    # Internal state storage
    _app: Optional[ctk.CTk] = field(default=None, init=False)
    _label: Optional[ctk.CTkLabel] = field(default=None, init=False)
    _thread: Optional[threading.Thread] = field(default=None, init=False)
    _is_running: bool = field(default=False, init=False)

    def start(self):
        """Starts the UI in a separate daemon thread."""
        if self._is_running:
            return
        
        self._is_running = True
        self._thread = threading.Thread(target=self._run_ui, daemon=True)
        self._thread.start()

    def _run_ui(self):
        ctk.set_appearance_mode("Dark")
        self._app = ctk.CTk()
        self._app.title(self.window_title)
        self._app.geometry("300x150")
        
        # UI Elements
        self._label = ctk.CTkLabel(self._app, text=self.initial_text, font=("Arial", 16))
        self._label.pack(pady=20, padx=20)
        
        # Close handler
        self._app.protocol("WM_DELETE_WINDOW", self.stop)

        # Start polling the queue
        self._app.after(100, self._process_queue)
        self._app.mainloop()


    def _process_queue(self):
        """Polls the queue for commands from the main thread."""
        try:
            while True:
                # Non-blocking get
                msg_type, msg_data = self._msg_queue.get_nowait()
                
                if msg_type == "TEXT":
                    if self._label:
                        self._label.configure(text=msg_data)
                
                elif msg_type == "VISIBLE":
                    if self._app:
                        if msg_data:
                            self._app.deiconify() # Show
                        else:
                            self._app.withdraw()  # Hide
                            
                elif msg_type == "STOP":
                    if self._app:
                        self._app.quit()
                        self._app.destroy()
                    self._is_running = False
                    return # Exit the loop

        except queue.Empty:
            pass
        
        # Schedule next check if still running
        if self._is_running and self._app:
            self._app.after(100, self._process_queue)

    # --- Public Callable Functions (Thread-Safe) ---

    def update_text(self, new_text: str):
        """Updates the text on the UI."""
        self._msg_queue.put(("TEXT", new_text))

    def set_visibility(self, visible: bool):
        """Toggles UI visibility (True = ON, False = OFF)."""
        self._msg_queue.put(("VISIBLE", visible))

    def stop(self):
        """Stops the UI thread safely."""
        self._msg_queue.put(("STOP", None))


# --- usage_example.py ---
if __name__ == "__main__":
    # 1. Initialize the dataclass
    ui = AsyncCTkUI(window_title="Threaded Dashboard")
    
    print("[Main] Starting UI thread...")
    ui.start()
    
    # Simulate main thread work
    try:
        time.sleep(2)
        print("[Main] Updating text...")
        ui.update_text("Processing Data: 10%")
        
        time.sleep(2)
        print("[Main] Hiding UI...")
        ui.set_visibility(False)
        
        time.sleep(2)
        print("[Main] Showing UI and updating...")
        ui.update_text("Processing Complete!")
        ui.set_visibility(True)
        
        # Keep main thread alive to observe the UI
        time.sleep(3)
        
    except KeyboardInterrupt:
        pass
    finally:
        print("[Main] Stopping UI.")
        ui.stop()