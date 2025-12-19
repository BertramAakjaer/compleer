import re

from spellchecker import SpellChecker


class WordValidator:
    def __init__(self):
        self.dictionary = SpellChecker()
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

        # 4. Check Dictionary or Custom List
        if word in self.custom_words:
            return True
        
        if self.dictionary.known([word]):
            return True

        # 5. Fallback: If it's not known but looks "word-like", maybe keep it?
        # For now, let's be strict:
        return False