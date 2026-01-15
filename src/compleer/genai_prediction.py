import os
from dotenv import load_dotenv
from dataclasses import dataclass, field
from google import genai
from google.genai import types

@dataclass
class GenAIRequestHandeler:
    api_key: str | None = field(default=None, repr=False)
    model_id: str = "gemma-3-4b-it"
    
    _client: genai.Client = field(init=False, repr=False)

    def __post_init__(self):
        resolved_key = self.api_key or os.environ.get("GOOGLE_API_KEY")
        if not resolved_key:
            raise ValueError("API Key must be provided.")
        self.api_key = resolved_key
        self._client = genai.Client(api_key=self.api_key)
        

    def predict_completion(self, context_text: str, incomplete_sentence: str, temperature: float = 0.3) -> str:
        try:
            full_prompt = (
                "INSTRUCTIONS: You are a precise text completion engine. "
                "Complete the last sentence logically based on the context. "
                "Do NOT repeat the start of the sentence. "
                "Output ONLY the completion text.\n\n"
                f"PREVIOUS CONTEXT:\n{context_text}\n\n"
                f"UNFINISHED SENTENCE:\n{incomplete_sentence}\n\n"
                "COMPLETION:"
            )

            config = types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=100
            )

            response = self._client.models.generate_content(
                model=self.model_id,
                contents=full_prompt,
                config=config
            )
            
            if response.text:
                return response.text.strip()
            return "" 

        except Exception as e:
            return f"Error: {str(e)}"