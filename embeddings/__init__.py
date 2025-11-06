"""Embeddings package for Local Recall."""
from embeddings.ollama_embeddings import OllamaEmbeddings, embedder
from embeddings.pipeline import EmbeddingPipeline, pipeline

__all__ = ["OllamaEmbeddings", "embedder", "EmbeddingPipeline", "pipeline"]
