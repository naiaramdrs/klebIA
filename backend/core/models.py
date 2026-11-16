import os
from types import SimpleNamespace
import google.generativeai as genai
from openai import OpenAI
from core.embeddings import GeminiEmbeddings, OpenAIEmbeddings

class OpenAIModel:
    # Mesma interface do GenerativeModel do Gemini: generate_content(prompt).text
    def __init__(self, model_name):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name

    def generate_content(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            reasoning_effort="low",
        )
        return SimpleNamespace(text=response.choices[0].message.content)

def get_provider(var_name):
    return os.getenv(var_name, "openai").lower()

def get_model():
    if get_provider("LLM_PROVIDER") == "gemini":
        genai.configure(api_key=os.getenv("API_KEY_GEMINI"))
        return genai.GenerativeModel('gemini-2.5-flash')
    return OpenAIModel('gpt-6-luna')

def get_embeddings_model():
    # Precisa ser o mesmo provedor usado para indexar o Chroma
    if get_provider("EMBEDDING_PROVIDER") == "gemini":
        return GeminiEmbeddings()
    return OpenAIEmbeddings()
