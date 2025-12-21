import re


from typing import Any
import queue
from pynput import keyboard
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class WordValidator:
    key_press_queue: queue.Queue
    word_queue: queue.Queue

    def __call__(self) -> None:
        buffer = []
        while True:
            key = self.key_press_queue.get()
            # Logic: If space/enter, send buffer to next queue
            if key == keyboard.Key.space:
                word = "".join(buffer)
                self.word_queue.put(word)
                buffer = []
            elif hasattr(key, 'char') and key.char:
                buffer.append(key.char)
            # Handle Backspace
            elif key == keyboard.Key.backspace and buffer:
                buffer.pop()





class WordValidator2:
    def __init__(self):
        self.custom_words = {"nrf", "kube-master", "dev-prod"} # Your nicknames
        
    def is_valid(self, word):
        # 1. Clean the word
        word = word.lower().strip()
        
        # 2. Basic Length & Character Check
        if len(word) < 2 or len(word) > 25:
            return False
            
        # 3. Reject Key Smashing (Repeated chars or no vowels)
        if re.search(r'(.)\1{3,}', word): # Blocks "aaaaa"
            return False
        if not any(vowel in word for vowel in "aeiouy1234567890"): # Blocks "bcdfgh"
            return False



        # 5. Fallback: If it's not known but looks "word-like", maybe keep it?
        # For now, let's be strict:
        return False
    
    


import re

class GibberishDetector:
    def __init__(self):
        # 1. SYNTAX: Code symbols and mixed numbers/letters
        self.code_syntax = re.compile(r'[<>\[\]\{\}\(\)#@_\\|~]')
        self.mixed_alphanum = re.compile(r'(?:[a-zA-Z]\d)|(?:\d[a-zA-Z])')
        
        # 2. KEYBOARD WALKS: Common adjacent keys
        self.keyboard_walks = re.compile(r'(asdf|qwer|zxcv|jkl;|1234|5678|hjkl)', re.IGNORECASE)
        
        # 3. LINGUISTICS: Vowels (y is a vowel here to help 'Rhythm'/'Strengths')
        self.vowels_re = re.compile(r'[aeiouyæøå]', re.IGNORECASE)

    def is_valid_text(self, text):
        clean = text.strip()
        if not clean: return False, "Empty"
        
        # --- LAYER 1: Code & Passwords ---
        if self.code_syntax.search(clean):
            return False, "Code Syntax"
        if self.mixed_alphanum.search(clean):
            return False, "Mixed Alphanum"

        # --- LAYER 2: Repetition ---
        if len(clean) > 3:
            unique_chars = len(set(clean))
            uniqueness_ratio = unique_chars / len(clean)
            if uniqueness_ratio < 0.5: 
                return False, "Repetitive / Low Entropy"

        # --- LAYER 3: Keyboard Walks ---
        if self.keyboard_walks.search(clean):
            return False, "Keyboard Walk"

        # --- LAYER 4: Linguistics (The "Angstskrig" Update) ---
        if not any(char.isdigit() for char in clean): 
            vowels_count = len(self.vowels_re.findall(clean))
            
            if vowels_count == 0:
                return False, "No Vowels"

            # Check Consonant Clusters
            consonant_groups = self.vowels_re.split(clean)
            max_consonants = max(len(g) for g in consonant_groups)
            
            # UPDATED: Limit raised from 6 to 7
            # 'Angstskrig' has 7 (ngstskr).
            # 'asdfghjkl' has 9.
            if max_consonants > 7:
                return False, "Consonant Cluster > 7"

        return True, "Valid Language"

# --- Final Verification ---
detector = GibberishDetector()

inputs = [
    "asdfghjkl",        # The previous failure
    "qwerty",           # Another walk
    "Strengths",        # Hard English word
    "Angstskrig",       # Hard Danish word
    "Sprængt",          # Low vowel density Danish
    "dk2#9!xA",         # Random
    "aaaaa",
    "12345",
    "Hello",
    "world",
    "Hej",
    "med",
    "dig",
    "Computermus",
    "print(x)",
    "wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",      # PASS
    "I",
    "am",
    "20",        # PASS (Numbers separated by space are okay)
    "kage123",
    "user_name" # Fails (Mixed Alphanum)
]

print(f"{'Text':<15} | {'Verdict':<10} | {'Reason'}")
print("-" * 55)

for t in inputs:
    valid, reason = detector.is_valid_text(t)
    verdict = "MATCH" if valid else "IGNORE"
    print(f"{t:<15} | {verdict:<10} | {reason}")