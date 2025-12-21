import pywinctl as pwc
import time

# Optional: Wait a moment to focus a different window before running
while True:
    time.sleep(2) 

    try:
        active_window = pwc.getActiveWindow()
        if active_window:
            print(f"Active Window Title: [{active_window.title}]")
        else:
            print("No active window found.")
    except Exception as e:
        print(f"Error: {e}")