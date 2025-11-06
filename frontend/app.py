"""Streamlit dashboard for Local Recall."""
import streamlit as st
import httpx
import asyncio
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from config import settings
from utils import document_parser
from database import db


# API base URL
API_BASE = f"http://localhost:{settings.BACKEND_PORT}"


def init_session_state():
    """Initialize session state variables."""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []


def get_status():
    """Get system status from API."""
    try:
        response = httpx.get(f"{API_BASE}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")
    return None


def start_capture():
    """Start data capture."""
    try:
        response = httpx.post(f"{API_BASE}/control/start", timeout=5)
        if response.status_code == 200:
            st.success("Capture started")
            st.rerun()
    except Exception as e:
        st.error(f"Error starting capture: {e}")


def stop_capture():
    """Stop data capture."""
    try:
        response = httpx.post(f"{API_BASE}/control/stop", timeout=5)
        if response.status_code == 200:
            st.success("Capture stopped")
            st.rerun()
    except Exception as e:
        st.error(f"Error stopping capture: {e}")


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Local Recall",
        page_icon="🧠",
        layout="wide"
    )

    init_session_state()

    st.title("🧠 Local Recall Dashboard")
    st.markdown("*Privacy-preserving local text capture and RAG system*")

    # Sidebar for system control and stats
    with st.sidebar:
        st.header("System Control")

        status = get_status()

        if status:
            is_capturing = status.get('capturing', False)

            if is_capturing:
                st.success("✅ Capture Active")
                if st.button("⏸️ Stop Capture", use_container_width=True):
                    stop_capture()
            else:
                st.warning("⏸️ Capture Paused")
                if st.button("▶️ Start Capture", use_container_width=True):
                    start_capture()

            st.divider()

            st.header("Statistics")
            db_stats = status.get('database', {})
            st.metric("Total Entries", db_stats.get('total_entries', 0))
            st.metric("Embedded Entries", db_stats.get('embedded_entries', 0))
            st.metric("Pending Embeddings", db_stats.get('pending_embeddings', 0))

            st.divider()

            st.header("Vector Store")
            vs_stats = status.get('vector_store', {})
            st.metric("Total Vectors", vs_stats.get('total_vectors', 0))
            st.metric("Dimension", vs_stats.get('dimension', 0))

        else:
            st.error("Backend not available")
            st.info("Start the backend with: `python backend/api.py`")

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search & Query", "📊 Data Browser", "📁 Upload", "⚙️ Settings"])

    with tab1:
        st.header("Semantic Search & RAG")

        query = st.text_input("Enter your query:", placeholder="What are you looking for?")

        col1, col2 = st.columns([1, 1])

        with col1:
            use_rag = st.checkbox("Use RAG (LLM-powered answers)", value=True)

        with col2:
            num_results = st.slider("Number of results", 1, 10, 5)

        if st.button("🔍 Search", type="primary", use_container_width=True):
            if query:
                with st.spinner("Searching..."):
                    try:
                        if use_rag:
                            response = httpx.post(
                                f"{API_BASE}/query",
                                json={"query": query, "model": settings.LLM_MODEL},
                                timeout=120  # Increased timeout for LLM calls
                            )
                        else:
                            response = httpx.post(
                                f"{API_BASE}/query",
                                json={"query": query, "k": num_results},
                                timeout=60  # Increased timeout for embedding generation
                            )

                        if response.status_code == 200:
                            result = response.json()

                            if use_rag:
                                st.subheader("Answer")
                                st.markdown(result.get('answer', 'No answer generated'))

                                sources = result.get('sources', [])
                                if not sources:
                                    st.info("No data found. Capture some text first using Ctrl+Alt+R or upload documents.")
                                else:
                                    st.subheader("Sources")
                                    for source in sources:
                                        with st.expander(f"Entry #{source['id']} (Score: {source['score']:.3f})"):
                                            entry_data = httpx.get(f"{API_BASE}/data?id={source['id']}").json()
                                            if entry_data:
                                                st.text(entry_data[0]['content'])
                                                st.caption(f"Source: {entry_data[0].get('source', 'Unknown')} | {entry_data[0].get('timestamp', '')}")
                            else:
                                results = result.get('results', [])
                                if not results:
                                    st.info("No results found. Capture some text first using Ctrl+Alt+R or upload documents.")
                                else:
                                    st.subheader(f"Found {len(results)} Results")
                                    for res in results:
                                        with st.expander(f"Entry #{res['id']} (Score: {res['score']:.3f})"):
                                            st.text(res['text'])
                                            st.caption(f"Source: {res.get('source', 'Unknown')} | {res.get('timestamp', '')}")
                        else:
                            st.error(f"Search failed: {response.status_code}")
                    except Exception as e:
                        st.error(f"Error during search: {e}")
            else:
                st.warning("Please enter a query")

    with tab2:
        st.header("Data Browser")

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_source = st.text_input("Filter by source:", placeholder="e.g., clipboard")
        with col2:
            filter_tag = st.text_input("Filter by tag:", placeholder="e.g., important")
        with col3:
            limit = st.number_input("Limit", min_value=10, max_value=500, value=50)

        if st.button("Load Entries", use_container_width=True):
            try:
                params = {"limit": limit}
                if filter_source:
                    params["source"] = filter_source
                if filter_tag:
                    params["tag"] = filter_tag

                response = httpx.get(f"{API_BASE}/data", params=params, timeout=10)

                if response.status_code == 200:
                    entries = response.json()
                    st.success(f"Loaded {len(entries)} entries")

                    for entry in entries:
                        with st.expander(f"Entry #{entry['id']} - {entry.get('source', 'Unknown')} ({entry.get('timestamp', '')})"):
                            st.text_area("Content", entry['content'], height=100, key=f"entry_{entry['id']}")
                            st.caption(f"Method: {entry.get('capture_method', 'Unknown')} | Tags: {', '.join(entry.get('tags', []))}")

                            if st.button(f"Delete", key=f"delete_{entry['id']}"):
                                delete_response = httpx.delete(f"{API_BASE}/data/{entry['id']}")
                                if delete_response.status_code == 200:
                                    st.success("Entry deleted")
                                    st.rerun()
                else:
                    st.error("Failed to load entries")
            except Exception as e:
                st.error(f"Error loading entries: {e}")

    with tab3:
        st.header("Upload Documents")

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'pdf', 'docx'],
            help="Upload TXT, PDF, or DOCX files"
        )

        tags_input = st.text_input("Tags (comma-separated):", placeholder="e.g., work, important")

        if uploaded_file and st.button("📤 Upload & Process", type="primary", use_container_width=True):
            with st.spinner("Processing document..."):
                try:
                    # Save uploaded file temporarily
                    temp_path = Path(f"./temp_{uploaded_file.name}")
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Parse document
                    content = document_parser.parse_file(str(temp_path))

                    # Clean up temp file
                    temp_path.unlink()

                    if content:
                        # Add to database via API
                        tags = [t.strip() for t in tags_input.split(",")] if tags_input else []
                        response = httpx.post(
                            f"{API_BASE}/data",
                            json={
                                "text": content,
                                "source": uploaded_file.name,
                                "tags": tags
                            },
                            timeout=10
                        )

                        if response.status_code == 200:
                            st.success(f"Successfully uploaded {uploaded_file.name}")
                            st.info(f"Extracted {len(content)} characters")
                        else:
                            st.error("Failed to save to database")
                    else:
                        st.error("Failed to extract text from document")

                except Exception as e:
                    st.error(f"Error processing document: {e}")

    with tab4:
        st.header("Settings")

        st.subheader("Keybinds")
        st.info("Keybinds allow you to quickly capture text without leaving your workflow")

        try:
            keybinds_response = httpx.get(f"{API_BASE}/keybinds", timeout=5)
            if keybinds_response.status_code == 200:
                keybinds = keybinds_response.json()

                if keybinds:
                    for kb in keybinds:
                        st.code(f"{kb['action']}: {kb['key_sequence']}")
                else:
                    st.warning("No keybinds configured")

                st.markdown("**Add New Keybind**")
                col1, col2 = st.columns(2)
                with col1:
                    action = st.selectbox("Action", ["capture_selected", "capture_screenshot"])
                with col2:
                    key_seq = st.text_input("Key Sequence", placeholder="<ctrl>+<alt>+r")

                if st.button("Add Keybind"):
                    if key_seq:
                        endpoint = "/keybind/selected" if action == "capture_selected" else "/keybind/screenshot"
                        response = httpx.post(
                            f"{API_BASE}{endpoint}",
                            json={"key_sequence": key_seq}
                        )
                        if response.status_code == 200:
                            st.success("Keybind added")
                            st.rerun()
        except Exception as e:
            st.error(f"Error loading keybinds: {e}")

        st.divider()

        st.subheader("Configuration")
        st.code(f"Embedding Model: {settings.EMBEDDING_MODEL}")
        st.code(f"LLM Model: {settings.LLM_MODEL}")
        st.code(f"Database: {settings.DATABASE_PATH}")
        st.code(f"FAISS Index: {settings.FAISS_INDEX_PATH}")


if __name__ == "__main__":
    main()
