import google.generativeai as genai
from typing import Generator, Optional

class GoogleGeminiClient:
    def __init__(self, api_key: str, model: str = "gemma-3n-e4b-it"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
    
    def generate(self, prompt: str) -> str:
        """Generate response from Gemini"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return "Error generating response"
    
    def generate_stream(self, prompt: str) -> Generator[str, None, None]:
        """Stream response from Gemini"""
        try:
            response = self.model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            print(f"Error in streaming: {e}")
            yield "Error generating response"

