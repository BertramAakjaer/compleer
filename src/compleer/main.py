import queue
import threading
from pynput import keyboard

from compleer.key_grabber import KeyGrabber

# Communication Channels
raw_input_queue = queue.Queue()
word_queue = queue.Queue()

# Thread Objects
key_grabber = KeyGrabber(raw_input_queue) # Thread 1

# --- THREAD 2: PARSER ---
def parser_thread():
    buffer = []
    while True:
        key = raw_input_queue.get()
        # Logic: If space/enter, send buffer to next queue
        if key == keyboard.Key.space:
            word = "".join(buffer)
            word_queue.put(word)
            buffer = []
        elif hasattr(key, 'char') and key.char:
            buffer.append(key.char)
        # Handle Backspace
        elif key == keyboard.Key.backspace and buffer:
            buffer.pop()

# --- THREAD 3: ANALYZER ---
def analyzer_thread():
    while True:
        word = word_queue.get()
        # Your validation logic here
        if len(word) > 2: 
            print(f"Analyzing word: {word}")
        word_queue.task_done()


def main():
    threads = [
        threading.Thread(target=key_grabber, daemon=True),
        threading.Thread(target=parser_thread, daemon=True),
        threading.Thread(target=analyzer_thread, daemon=True)
    ]
    
    for t in threads:
        t.start()

    # Keep main thread alive
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")

if __name__ == "__main__":
    main()