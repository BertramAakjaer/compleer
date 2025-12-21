from typing import Any
import queue
from pynput import keyboard
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class KeyGrabber:
    key_press_queue: queue.Queue

    def __call__(self) -> None:
        def on_press(key):
            self.key_press_queue.put(key)
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()