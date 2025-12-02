"""FAISS vector store for semantic search."""
import numpy as np
import faiss
import json
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass

from config import settings


logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result with score."""
    entry_id: int
    score: float
    distance: float


class FAISSVectorStore:
    """FAISS-based vector store for embeddings."""

    def __init__(self, index_path: str = None, dimension: int = None):
        """Initialize FAISS vector store."""
        self.index_path = Path(index_path or settings.FAISS_INDEX_PATH)
        self.dimension = dimension or settings.EMBEDDING_DIMENSION
        self.index = None
        self.id_map = []  # Maps FAISS index positions to database entry IDs

        # Ensure index directory exists
        self.index_path.mkdir(parents=True, exist_ok=True)

        self._initialize_index()

    def _initialize_index(self):
        """Initialize or load FAISS index."""
        index_file = self.index_path / "index.faiss"
        id_map_file = self.index_path / "id_map.json"

        if index_file.exists() and id_map_file.exists():
            try:
                self.index = faiss.read_index(str(index_file))
                with open(id_map_file, "r", encoding="utf-8") as f:
                    self.id_map = json.load(f)
                logger.info(f"Loaded FAISS index with {len(self.id_map)} vectors")
            except Exception as e:
                logger.error(f"Error loading FAISS index: {e}")
                self._create_new_index()
        else:
            self._create_new_index()

    def _create_new_index(self):
        """Create a new FAISS index."""
        # Use L2 distance for similarity
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_map = []
        logger.info(f"Created new FAISS index with dimension {self.dimension}")

    def add_embedding(self, entry_id: int, embedding: np.ndarray) -> int:
        """Add an embedding to the index."""
        if embedding.shape[0] != self.dimension:
            raise ValueError(f"Embedding dimension {embedding.shape[0]} doesn't match index dimension {self.dimension}")

        # Ensure embedding is 2D for FAISS
        if len(embedding.shape) == 1:
            embedding = embedding.reshape(1, -1)

        # Normalize embedding for cosine similarity
        faiss.normalize_L2(embedding)

        # Add to index
        self.index.add(embedding.astype('float32'))
        faiss_id = len(self.id_map)
        self.id_map.append(entry_id)

        logger.debug(f"Added embedding for entry {entry_id} at FAISS position {faiss_id}")
        return faiss_id

    def add_embeddings_batch(self, entry_ids: List[int], embeddings: np.ndarray) -> List[int]:
        """Add multiple embeddings in batch."""
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension {embeddings.shape[1]} doesn't match index dimension {self.dimension}")

        # Normalize embeddings
        faiss.normalize_L2(embeddings)

        # Add to index
        self.index.add(embeddings.astype('float32'))

        # Update ID map
        start_id = len(self.id_map)
        self.id_map.extend(entry_ids)

        faiss_ids = list(range(start_id, start_id + len(entry_ids)))
        logger.info(f"Added {len(entry_ids)} embeddings in batch")
        return faiss_ids

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[SearchResult]:
        """Search for similar embeddings."""
        if self.index.ntotal == 0:
            logger.warning("Index is empty, returning no results")
            return []

        # Ensure query is 2D
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Normalize query
        faiss.normalize_L2(query_embedding)

        # Search
        k = min(k, self.index.ntotal)  # Don't request more than available
        distances, indices = self.index.search(query_embedding.astype('float32'), k)

        # Convert to search results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.id_map):
                entry_id = self.id_map[idx]
                # Convert L2 distance to similarity score (0-1, higher is better)
                score = 1.0 / (1.0 + distance)
                results.append(SearchResult(
                    entry_id=entry_id,
                    score=score,
                    distance=float(distance)
                ))

        return results

    def save(self):
        """Save index to disk."""
        self.index_path.mkdir(parents=True, exist_ok=True)

        index_file = self.index_path / "index.faiss"
        id_map_file = self.index_path / "id_map.json"

        faiss.write_index(self.index, str(index_file))

        with open(id_map_file, "w", encoding="utf-8") as f:
            json.dump(self.id_map, f)

        logger.info(f"Saved FAISS index with {len(self.id_map)} vectors to {self.index_path}")

    def delete_entry(self, entry_id: int) -> bool:
        """Remove an entry from the index (by rebuilding)."""
        # FAISS doesn't support deletion, so we need to rebuild
        # For alpha version, we'll mark this as a TODO
        logger.warning("Entry deletion requires index rebuild - not implemented in alpha")
        return False

    def get_stats(self) -> dict:
        """Get index statistics."""
        return {
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "index_path": str(self.index_path)
        }

    def reset(self):
        """Reset the vector store (clear all embeddings)."""
        logger.info("Resetting FAISS vector store...")
        self._create_new_index()
        # Delete saved index files if they exist
        index_file = self.index_path / "index.faiss"
        id_map_file = self.index_path / "id_map.json"
        # Also clean up legacy pickle file if it exists
        legacy_id_map_file = self.index_path / "id_map.pkl"

        if index_file.exists():
            index_file.unlink()
        if id_map_file.exists():
            id_map_file.unlink()
        if legacy_id_map_file.exists():
            legacy_id_map_file.unlink()

        logger.info("FAISS vector store reset complete")


# Global vector store instance
vector_store = FAISSVectorStore()
