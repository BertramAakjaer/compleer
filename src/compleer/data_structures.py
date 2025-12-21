import time
from dataclasses import dataclass, field



###############################
def to_days(days: int) -> int:
    return days * 60 * 60 * 24

MAX_AGE: int = to_days(30)
###############################


def current_time_sec() -> int:
    return int(time.time())


@dataclass(slots=True, frozen=True)
class Sentence:
    words_arr: list[str]
    sentence: str
    words: int
    tokens: int
    
    # Automatically handeled
    created_at: int = field(default_factory=current_time_sec)

@dataclass(slots=True, frozen=True)
class ProgramSentences:
    sentence_fifo: list[Sentence]
    program_title: str
    
    def prune_old_sentences(self) -> None:
        curr_time = current_time_sec()
        
        while self.sentence_fifo:
            sentence = self.sentence_fifo[0]
            
            if (curr_time - sentence.created_at) > MAX_AGE:
                self.sentence_fifo.pop(0)
            else:
                break
        
    
@dataclass(slots=True, frozen=True)
class ProgramCollection:
    programs: dict[str, ProgramSentences] = field(default_factory=dict, init=False)

    def add_sentence(self, program_title: str, words: list[str]) -> None:
        no_space_punct = {'.', ',', '!', '?', ':', ';'}
        stentence_string = words[0]
        
        for word in words[1:]: # Doesn't make space between ending symbol and word
            if word == words[-1] and word in no_space_punct:
                stentence_string += word
            else:
                stentence_string += " " + word

        new_sentence = Sentence(words_arr=words, sentence=stentence_string, words=len(words), tokens=len(stentence_string))

        if program_title in self.programs:
            self.programs[program_title].sentence_fifo.append(new_sentence)
        else:
            new_program = ProgramSentences(
                program_title=program_title,
                sentence_fifo=[new_sentence],
            )
            self.programs[program_title] = new_program
        
        print(f"Added following sentence to data:\n-\t{stentence_string}\n-\tAdded for [{program_title}]")    
    
    def get_sentences(self, program_title: str, max_tokens: int) -> list[Sentence]:
        if program_title not in self.programs:
            return []

        program = self.programs[program_title]
        
        program.prune_old_sentences()

        current_tokens = 0
        selected_buffer = []

        for sentence in reversed(program.sentence_fifo):
            if current_tokens + sentence.tokens <= max_tokens:
                selected_buffer.append(sentence)
                current_tokens += sentence.tokens
            else:
                break
        
        selected_buffer.reverse() # So the original context is kept
        return selected_buffer