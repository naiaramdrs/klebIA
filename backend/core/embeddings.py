import os
import google.generativeai as genai
from openai import OpenAI
from langchain_core.embeddings import Embeddings

class GeminiEmbeddings(Embeddings):
    def __init__(self):
        genai.configure(api_key=os.getenv("API_KEY_GEMINI"))
        self.model = "models/embedding-001"

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for text in texts:
            response = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document",
            )
            embeddings.append(response["embedding"])
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        response = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query",
        )
        return response["embedding"]


class OpenAIEmbeddings(Embeddings):
    def __init__(self, batch_size=100):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-3-small"
        self.batch_size = batch_size

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            response = self.client.embeddings.create(
                model=self.model,
                input=texts[i:i + self.batch_size],
            )
            embeddings.extend([item.embedding for item in response.data])
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        return response.data[0].embedding
