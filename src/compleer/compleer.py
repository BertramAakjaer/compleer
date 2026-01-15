from dataclasses import dataclass, field
import queue
import threading
import time

from compleer.key_grabber import KeyGrabber
from compleer.word_seperator import WordSeperator
from compleer.setence_collector import SentenceCollector
from compleer.prediction_engine import PredictionEngine

from compleer.data_structures import ProgramCollection

@dataclass(slots=True, frozen=True)
class CompleerApp:
    raw_input_queue: queue.Queue = field(default_factory=queue.Queue)
    word_queue: queue.Queue = field(default_factory=queue.Queue)
    
    data_storage: ProgramCollection = field(default_factory=ProgramCollection)
    
    # run as app() instead of app.run()
    def __call__(self) -> None:
        # Thread Objects
        key_grabber = KeyGrabber(self.raw_input_queue)
        word_seperator = WordSeperator(self.raw_input_queue, self.word_queue)
        sentence_collector = SentenceCollector(self.word_queue, self.data_storage)
        prediction_engine = PredictionEngine(self.data_storage, sentence_collector)

        threads = [
            threading.Thread(target=key_grabber, daemon=True),
            threading.Thread(target=word_seperator, daemon=True),
            threading.Thread(target=sentence_collector, daemon=True),
            threading.Thread(target=prediction_engine, daemon=True)
        ]

        for t in threads:
            t.start()

        # Keep main thread alive for not closing console
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")