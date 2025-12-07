"""RAG query engine for semantic search and generation."""
import logging
from typing import List, Dict, Any, Optional
import ollama
import asyncio
from concurrent.futures import ThreadPoolExecutor
from openai import AsyncOpenAI

from database import db
from vector_store import vector_store
from embeddings import embedder
from config import settings


logger = logging.getLogger(__name__)

# Thread pool for blocking Ollama calls
executor = ThreadPoolExecutor(max_workers=2)

# OpenAI client (initialized if API key is available)
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


class RAGQueryEngine:
    """RAG-based query engine for local data."""

    def __init__(self):
        """Initialize RAG query engine."""
        self.max_context_snippets = settings.MAX_CONTEXT_SNIPPETS
        self.llm_model = settings.LLM_MODEL

    def _is_openai_model(self, model: str) -> bool:
        """Check if the model is an OpenAI model."""
        openai_prefixes = ["gpt-", "o1-", "o3-"]
        return any(model.startswith(prefix) for prefix in openai_prefixes)

    async def semantic_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search over stored data."""
        try:
            # Check if vector store has data
            if vector_store.index.ntotal == 0:
                logger.warning("Vector store is empty, no results to return")
                return []

            # Generate query embedding
            query_embedding = await embedder.embed_async(query)

            # Search vector store
            search_results = vector_store.search(query_embedding, k=k)

            # Retrieve full entries from database
            results = []
            for result in search_results:
                entry = db.get_entry(result.entry_id)
                if entry:
                    results.append({
                        "id": entry.id,
                        "text": entry.content,
                        "score": float(result.score),  # Convert numpy.float32 to Python float
                        "source": entry.source,
                        "timestamp": entry.timestamp.isoformat() if entry.timestamp else None
                    })

            logger.info(f"Semantic search returned {len(results)} results for query: {query}")
            return results

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []

    async def query_with_rag(self, query: str, model: Optional[str] = None, k: Optional[int] = None) -> Dict[str, Any]:
        """Perform RAG-based query with LLM generation."""
        try:
            # Use provided k or fall back to default max_context_snippets
            num_results = k if k is not None else self.max_context_snippets

            # Perform semantic search
            search_results = await self.semantic_search(
                query,
                k=num_results
            )

            if not search_results:
                return {
                    "answer": "I don't have enough local context to answer this.",
                    "sources": [],
                    "query": query
                }

            # Build context from search results
            context_parts = []
            sources = []
            for i, result in enumerate(search_results):
                context_parts.append(f"[{result['id']}] {result['text']}")
                sources.append({
                    "id": result["id"],
                    "score": float(result["score"]),  # Ensure it's a Python float
                    "source": result.get("source"),
                    "timestamp": result.get("timestamp")
                })

            context = "\n\n".join(context_parts)

            # Build prompt
            system_prompt = (
                "You are a factual, privacy-preserving assistant operating entirely on local data. "
                "Answer the user's question using only the provided text snippets. "
                "Do not invent details or access external sources. "
                "If the context is insufficient, respond with: 'I don't have enough local context to answer this.' "
                "Keep responses under 150 words and cite snippet IDs in brackets."
            )

            user_prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"

            # Generate response using the appropriate LLM provider
            llm_model = model or self.llm_model

            if self._is_openai_model(llm_model):
                # Use OpenAI API
                if not openai_client:
                    return {
                        "answer": "OpenAI API key not configured. Please set OPENAI_API_KEY in your environment.",
                        "sources": sources,
                        "query": query
                    }

                logger.info(f"Calling OpenAI API with model: {llm_model}")

                response = await openai_client.chat.completions.create(
                    model=llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )

                answer = response.choices[0].message.content
            else:
                # Use Ollama (run in thread pool since it's blocking)
                logger.info(f"Calling Ollama with model: {llm_model}")

                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    executor,
                    lambda: ollama.chat(
                        model=llm_model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ]
                    )
                )

                answer = response['message']['content']

            logger.info(f"Generated RAG response for query: {query}")

            return {
                "answer": answer,
                "sources": sources,
                "query": query,
                "model": llm_model
            }

        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            error_msg = str(e)

            # Provide helpful error messages based on model type
            llm_model = model or self.llm_model
            if self._is_openai_model(llm_model):
                # OpenAI-specific error messages
                if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    error_msg = "OpenAI API key not configured or invalid. Please set OPENAI_API_KEY in your environment."
                else:
                    error_msg = f"OpenAI API error: {error_msg}. Make sure your API key is set in the environment."
            else:
                # Ollama-specific error messages
                if "connection" in error_msg.lower() or "connect" in error_msg.lower():
                    error_msg = "Could not connect to Ollama. Make sure Ollama is running (start with: ollama serve)"
                elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                    error_msg = f"Model '{llm_model}' not found. Pull it with: ollama pull {llm_model}"

            return {
                "answer": f"Error processing query: {error_msg}",
                "sources": [],
                "query": query
            }

    async def query_with_rag_stream(self, query: str, model: Optional[str] = None, k: Optional[int] = None):
        """Perform RAG-based query with LLM generation using streaming."""
        try:
            # Use provided k or fall back to default max_context_snippets
            num_results = k if k is not None else self.max_context_snippets

            # Perform semantic search
            search_results = await self.semantic_search(
                query,
                k=num_results
            )

            if not search_results:
                # Yield metadata first
                yield {
                    "type": "metadata",
                    "sources": [],
                    "query": query
                }
                # Yield answer
                yield {
                    "type": "answer",
                    "content": "I don't have enough local context to answer this."
                }
                return

            # Build context from search results
            context_parts = []
            sources = []
            for i, result in enumerate(search_results):
                context_parts.append(f"[{result['id']}] {result['text']}")
                sources.append({
                    "id": result["id"],
                    "score": float(result["score"]),
                    "source": result.get("source"),
                    "timestamp": result.get("timestamp")
                })

            context = "\n\n".join(context_parts)

            # Yield metadata first (sources)
            yield {
                "type": "metadata",
                "sources": sources,
                "query": query,
                "model": model or self.llm_model
            }

            # Build prompt
            system_prompt = (
                "You are a factual, privacy-preserving assistant operating entirely on local data. "
                "Answer the user's question using only the provided text snippets. "
                "Do not invent details or access external sources. "
                "If the context is insufficient, respond with: 'I don't have enough local context to answer this.' "
                "Keep responses under 150 words and cite snippet IDs in brackets."
            )

            user_prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"

            # Generate response using the appropriate LLM provider with streaming
            llm_model = model or self.llm_model

            if self._is_openai_model(llm_model):
                # Use OpenAI API streaming
                if not openai_client:
                    yield {
                        "type": "error",
                        "content": "OpenAI API key not configured. Please set OPENAI_API_KEY in your environment."
                    }
                    return

                logger.info(f"Calling OpenAI API with streaming for model: {llm_model}")

                stream = await openai_client.chat.completions.create(
                    model=llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500,
                    stream=True
                )

                async for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        yield {
                            "type": "answer_chunk",
                            "content": content
                        }
            else:
                # Use Ollama streaming
                logger.info(f"Calling Ollama with streaming for model: {llm_model}")

                loop = asyncio.get_event_loop()

                # Stream response chunks (Ollama is blocking, so run in executor)
                stream = ollama.chat(
                    model=llm_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    stream=True
                )

                for chunk in stream:
                    if 'message' in chunk and 'content' in chunk['message']:
                        content = chunk['message']['content']
                        yield {
                            "type": "answer_chunk",
                            "content": content
                        }

            # Signal completion
            yield {
                "type": "done"
            }

            logger.info(f"Completed streaming RAG response for query: {query}")

        except Exception as e:
            logger.error(f"Error in RAG streaming query: {e}")
            error_msg = str(e)

            # Provide helpful error messages based on model type
            llm_model = model or self.llm_model
            if self._is_openai_model(llm_model):
                # OpenAI-specific error messages
                if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
                    error_msg = "OpenAI API key not configured or invalid. Please set OPENAI_API_KEY in your environment."
                else:
                    error_msg = f"OpenAI API error: {error_msg}. Make sure your API key is set in the environment."
            else:
                # Ollama-specific error messages
                if "connection" in error_msg.lower() or "connect" in error_msg.lower():
                    error_msg = "Could not connect to Ollama. Make sure Ollama is running (start with: ollama serve)"
                elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                    error_msg = f"Model '{llm_model}' not found. Pull it with: ollama pull {llm_model}"

            yield {
                "type": "error",
                "content": f"Error processing query: {error_msg}"
            }


# Global query engine instance
query_engine = RAGQueryEngine()
