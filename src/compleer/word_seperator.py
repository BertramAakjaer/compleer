from dataclasses import dataclass, field
from pynput import keyboard
import queue
import re

@dataclass(slots=True, frozen=True)
class WordSeperator:
    raw_input_queue: queue.Queue
    word_queue: queue.Queue

    def __call__(self) -> None:
        buffer = []
        while True:
            try:
                key = self.raw_input_queue.get(timeout=3.0)
                
                if key in (keyboard.Key.space, keyboard.Key.enter, keyboard.Key.esc):
                    if buffer:
                        word = "".join(buffer)
                        if self.word_filter(word):
                            self.word_queue.put(word)
                        buffer = []
                
                elif hasattr(key, 'char') and key.char:
                    buffer.append(key.char)
                
                # Handle Backspace
                elif key == keyboard.Key.backspace and buffer:
                    buffer.pop()

            except queue.Empty:
                if buffer:
                    word = "".join(buffer)
                    if self.word_filter(word):
                        self.word_queue.put(word)
                    buffer = []
                    
    
    # True = Words is accepted, False = Words is discarded
    def word_filter(self, word: str) -> bool:
        code_syntax = re.compile(r'[<>\[\]\{\}\(\)#@_\\|~]')
        mixed_alphanum = re.compile(r'(?:[a-zA-Z]\d)|(?:\d[a-zA-Z])')
        keyboard_walks = re.compile(r'(asdf|qwer|zxcv|jkl;|1234|5678|hjkl)', re.IGNORECASE)
        vowels_re = re.compile(r'[aeiouyæøå]', re.IGNORECASE)
        
        
        clean = word.strip()
        if not clean:
            return False
        
        # --- LAYER 1: Code & Passwords ---
        if code_syntax.search(clean):
            return False
        if mixed_alphanum.search(clean):
            return False

        # --- LAYER 2: Repetition ---
        if len(clean) > 3:
            unique_chars = len(set(clean))
            uniqueness_ratio = unique_chars / len(clean)
            if uniqueness_ratio < 0.5: 
                return False

        # --- LAYER 3: Keyboard Walks ---
        if keyboard_walks.search(clean):
            return False

        # --- LAYER 4: Linguistics ---
        if not any(char.isdigit() for char in clean): 
            vowels_count = len(vowels_re.findall(clean))
            
            if vowels_count == 0:
                return False

            # Check Consonant Clusters
            consonant_groups = vowels_re.split(clean)
            max_consonants = max(len(g) for g in consonant_groups)
            
            if max_consonants > 7:
                return False
        
        
        if len(word) == 1:
            if not (word == 'i' or word == 'å' or word == 'r' or word.isdigit()):
                return False

        print(f"Word: {word}, passed filter")
        return True