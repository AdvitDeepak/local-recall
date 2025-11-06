"""Embedding pipeline for processing and indexing data."""
import asyncio
import logging
from typing import List
from datetime import datetime

from database import db, DataEntry
from vector_store import vector_store
from embeddings.ollama_embeddings import embedder
from config import settings


logger = logging.getLogger(__name__)


class EmbeddingPipeline:
    """Pipeline for generating and indexing embeddings."""

    def __init__(self):
        """Initialize embedding pipeline."""
        self.is_running = False
        self.batch_size = settings.BATCH_SIZE

    async def process_pending_entries(self):
        """Process all pending entries that need embeddings."""
        logger.info("Starting embedding pipeline...")

        while self.is_running:
            try:
                # Get unembedded entries
                entries = db.get_unembedded_entries(limit=self.batch_size)

                if not entries:
                    logger.debug("No pending entries to embed")
                    await asyncio.sleep(5)  # Wait before checking again
                    continue

                logger.info(f"Processing {len(entries)} entries")

                # Extract texts and IDs
                texts = [entry.content for entry in entries]
                entry_ids = [entry.id for entry in entries]

                # Generate embeddings in batch
                embeddings = await embedder.embed_batch_async(texts)

                # Add to FAISS index
                faiss_ids = vector_store.add_embeddings_batch(entry_ids, embeddings)

                # Mark entries as embedded
                for entry_id, faiss_id in zip(entry_ids, faiss_ids):
                    db.mark_embedded(entry_id, faiss_id)

                # Save index
                vector_store.save()

                logger.info(f"Successfully embedded {len(entries)} entries")

            except Exception as e:
                logger.error(f"Error in embedding pipeline: {e}")
                await asyncio.sleep(10)  # Wait longer on error

        logger.info("Embedding pipeline stopped")

    async def start(self):
        """Start the embedding pipeline."""
        if self.is_running:
            logger.warning("Embedding pipeline already running")
            return

        self.is_running = True
        await self.process_pending_entries()

    def stop(self):
        """Stop the embedding pipeline."""
        logger.info("Stopping embedding pipeline...")
        self.is_running = False

    async def embed_single_entry(self, entry_id: int) -> bool:
        """Embed a single entry immediately."""
        try:
            entry = db.get_entry(entry_id)
            if not entry:
                logger.error(f"Entry {entry_id} not found")
                return False

            # Generate embedding
            embedding = await embedder.embed_async(entry.content)

            # Add to index
            faiss_id = vector_store.add_embedding(entry_id, embedding)

            # Mark as embedded
            db.mark_embedded(entry_id, faiss_id)

            # Save index
            vector_store.save()

            logger.info(f"Successfully embedded entry {entry_id}")
            return True

        except Exception as e:
            logger.error(f"Error embedding entry {entry_id}: {e}")
            return False


# Global pipeline instance
pipeline = EmbeddingPipeline()
