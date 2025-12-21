from dataclasses import dataclass, field

from compleer.data_structures import ProgramCollection
from compleer.setence_collector import SentenceCollector

@dataclass(slots=True)
class UI_handeler_data:    
    curr_sentence: SentenceCollector
    data_storage: ProgramCollection
    
    guess_ready: bool = field(default_factory=bool)
    
    def __call__(self) -> None:
        self.guess_ready = True