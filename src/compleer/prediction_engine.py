import os
import time
from dotenv import load_dotenv
from dataclasses import dataclass

from compleer.data_structures import ProgramCollection
from compleer.setence_collector import SentenceCollector
from compleer.genai_prediction import GenAIRequestHandeler

TIME_TO_PREDICT = 5
SLEEP_TIME = 0.2
MAX_TOKENS = 300

@dataclass(slots=True, frozen=True)
class PredictionEngine:
    data_storage: ProgramCollection
    sentence_col: SentenceCollector
    
    def __call__(self) -> None:
        last_title = None
        last_sentence = None
        last_time = None
        
        load_dotenv() 

        if not os.environ.get("GOOGLE_API_KEY"):
            print("Warning: GOOGLE_API_KEY not found in environment.")
            
        try:
            client = GenAIRequestHandeler() 
        except ValueError as e:
            print(f"Error: {e}")
        
        while True:
            if not last_title or not last_sentence or not last_time:
                last_title, last_sentence = self.sentence_col.get_curr_info()
                last_time = int(time.time())
                time.sleep(SLEEP_TIME)
                continue
            
            window_title, sentence = self.sentence_col.get_curr_info()
            
            if window_title == last_title and sentence == last_sentence:
                curr_time = int(time.time())
                if (curr_time - last_time) >= TIME_TO_PREDICT:
                    incomplete_sentence = sentence
                    previous_context = self.data_storage.get_sentences(window_title, MAX_TOKENS)
                    try:
                        text_prediction = client.predict_completion(context_text=previous_context, incomplete_sentence=incomplete_sentence)
                    except ValueError as e:
                        print(f"Error: {e}")
                        text_prediction = ""
                    print(f"Predicted text: {text_prediction}")
                    
                time.sleep(SLEEP_TIME)
                
            else:
                last_title, last_sentence = self.sentence_col.get_curr_info()
                last_time = int(time.time())
                time.sleep(SLEEP_TIME)