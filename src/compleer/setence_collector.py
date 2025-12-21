from dataclasses import dataclass, field
import queue
import pywinctl as pwc
import time

from compleer.data_structures import ProgramCollection

@dataclass(slots=True, frozen=True)
class SentenceCollector:
    word_queue: queue.Queue
    data_storage: ProgramCollection
    
    curr_sentence: list[str] = field(default_factory=list[str])
    
    def __call__(self) -> None:
        last_window_title = None
        
        while True:
            try:
                key = self.word_queue.get(timeout=20)
            except queue.Empty:
                if self.curr_sentence:
                    key = "."
                else:
                    continue
                
            
            active_window = pwc.getActiveWindow()
            current_window_title = active_window.title if active_window else None
            
            if (last_window_title is not None
                and 
                current_window_title is not None
                and 
                current_window_title != last_window_title
                and 
                self.curr_sentence):
                
                self.curr_sentence.append(".")
                self.data_storage.add_sentence(last_window_title, self.curr_sentence)
                self.curr_sentence.clear()

            if current_window_title is not None:
                last_window_title = current_window_title
            
            
            self.curr_sentence.append(key)
            
            line_enders = {'?', '!', '.', ':', ';'}
            if self.curr_sentence[-1][-1] in line_enders:
                
                # Splits the ending sign up so it doesn't lock into a word
                if not (len(self.curr_sentence[-1]) == 1):
                    temp = self.curr_sentence[-1][-1]
                    self.curr_sentence[-1] = self.curr_sentence[-1][:-1]
                    self.curr_sentence.append(temp)

                if not active_window:
                    time.sleep(0.5)
                    continue
                
                self.data_storage.add_sentence(active_window.title, self.curr_sentence)
                self.curr_sentence.clear()
                