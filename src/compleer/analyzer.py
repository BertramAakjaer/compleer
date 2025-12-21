
class TextProcessor:
    def __init__(self, input_queue):
        self.input_queue = input_queue
        self.current_buffer = []
        self.terminators = {'space', 'enter', 'Key.space', 'Key.enter', '\x1b'} # Esc

    def run(self):
        """The main loop for the analyzer thread."""
        while True:
            key = self.input_queue.get()
            if key is None:
                break  # Sentinel value to stop thread

            # Logic to handle word completion
            if key in self.terminators or len(key) > 1:
                word = "".join(self.current_buffer).strip()
                if word:
                    self.process_word(word)
                self.current_buffer = [] # Clear buffer for next word
            else:
                # Handle backspace
                if key == 'Key.backspace' and self.current_buffer:
                    self.current_buffer.pop()
                elif len(key) == 1: # Only add printable characters
                    self.current_buffer.append(key)

    def process_word(self, word):
        """Place your 'Understanding' or AI logic here."""
        print(f"DEBUG: Processing completed word -> {word}")
        # Example: if word == "nrf": trigger_completion("non-refundable")'
