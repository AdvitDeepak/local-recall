"""Ollama-based embedding generation."""
import asyncio
import logging
from typing import List, Optional
import numpy as np
import ollama

from config import settings


logger = logging.getLogger(__name__)


class OllamaEmbeddings:
    """Generate embeddings using Ollama."""

    def __init__(self, model: str = None, base_url: str = None):
        """Initialize Ollama embeddings."""
        self.model = model or settings.EMBEDDING_MODEL
        self.base_url = base_url or settings.OLLAMA_BASE_URL

        # Configure ollama client
        if self.base_url != "http://localhost:11434":
            ollama._client._base_url = self.base_url

    def embed(self, text: str) -> np.ndarray:
        """Generate embedding for a single text."""
        try:
            response = ollama.embeddings(
                model=self.model,
                prompt=text
            )
            embedding = np.array(response['embedding'], dtype='float32')
            logger.debug(f"Generated embedding of dimension {embedding.shape[0]}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            try:
                embedding = self.embed(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error embedding text: {e}")
                # Use zero vector as fallback
                embeddings.append(np.zeros(settings.EMBEDDING_DIMENSION, dtype='float32'))

        return np.array(embeddings)

    async def embed_async(self, text: str) -> np.ndarray:
        """Generate embedding asynchronously."""
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.embed, text)

    async def embed_batch_async(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts asynchronously."""
        tasks = [self.embed_async(text) for text in texts]
        embeddings = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        result = []
        for i, emb in enumerate(embeddings):
            if isinstance(emb, Exception):
                logger.error(f"Error embedding text {i}: {emb}")
                result.append(np.zeros(settings.EMBEDDING_DIMENSION, dtype='float32'))
            else:
                result.append(emb)

        return np.array(result)

    def check_model_available(self) -> bool:
        """Check if the embedding model is available."""
        try:
            ollama.list()
            # Try to generate a test embedding
            self.embed("test")
            return True
        except Exception as e:
            logger.error(f"Embedding model not available: {e}")
            return False


# Global embeddings instance
embedder = OllamaEmbeddings()
