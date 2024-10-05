import logging
from groq import Groq

logging.basicConfig(level=logging.INFO)
Logger = logging.getLogger(__name__)

class GroqAPIWrapper:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    def query(self, prompt: str, model: str = "llama3-8b-8192") -> str:
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            Logger.error(f"Error querying Groq API: {str(e)}")
            raise Exception(f"Failed to get response from Groq API: {str(e)}")