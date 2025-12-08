"""Streamlit dashboard for Local Recall."""
import streamlit as st
import httpx
import asyncio
from datetime import datetime
from pathlib import Path
import sys
import json
import time

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
    if 'last_notification_id' not in st.session_state:
        st.session_state.last_notification_id = 0
    if 'notifications_enabled' not in st.session_state:
        st.session_state.notifications_enabled = True
    if 'last_poll_time' not in st.session_state:
        st.session_state.last_poll_time = 0
    if 'last_entry_count' not in st.session_state:
        st.session_state.last_entry_count = 0


def fetch_new_notifications():
    """Fetch new notifications from the API."""
    try:
        response = httpx.get(
            f"{API_BASE}/notifications",
            params={
                "since_id": st.session_state.last_notification_id,
                "unread_only": True,
                "limit": 5
            },
            timeout=3
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("notifications", [])
    except Exception:
        pass
    return []


def display_notifications():
    """Display notification toasts for capture events."""
    if not st.session_state.notifications_enabled:
        return False

    notifications = fetch_new_notifications()
    displayed_any = False

    for notif in notifications:
        # Update the last seen notification ID
        if notif["id"] > st.session_state.last_notification_id:
            st.session_state.last_notification_id = notif["id"]

        # Display notification based on status
        status = notif.get("status", "info")
        title = notif.get("title", "Notification")
        message = notif.get("message", "")

        # Format the notification message
        full_message = f"**{title}**\n\n{message}"

        if status == "success":
            st.toast(full_message, icon="✅")
        elif status == "warning":
            st.toast(full_message, icon="⚠️")
        elif status == "error":
            st.toast(full_message, icon="❌")
        else:
            st.toast(full_message, icon="ℹ️")

        displayed_any = True

        # Mark notification as read
        try:
            httpx.post(f"{API_BASE}/notifications/{notif['id']}/read", timeout=2)
        except Exception:
            pass

    return displayed_any


@st.fragment(run_every=2)
def auto_refresh_notifications():
    """Auto-refresh fragment that checks for new notifications every 2 seconds."""
    if not st.session_state.notifications_enabled:
        st.empty()
        return

    # Check if there are new notifications
    has_new_success = False
    try:
        response = httpx.get(
            f"{API_BASE}/notifications",
            params={
                "since_id": st.session_state.last_notification_id,
                "unread_only": True,
                "limit": 5
            },
            timeout=2
        )
        if response.status_code == 200:
            data = response.json()
            notifications = data.get("notifications", [])

            for notif in notifications:
                # Update the last seen notification ID
                if notif["id"] > st.session_state.last_notification_id:
                    st.session_state.last_notification_id = notif["id"]

                # Display notification based on status
                status = notif.get("status", "info")
                title = notif.get("title", "Notification")
                message = notif.get("message", "")

                # Check if this is a successful capture
                if status == "success":
                    has_new_success = True

                # Use st.toast for popup notifications
                full_message = f"**{title}**\n\n{message}"

                if status == "success":
                    st.toast(full_message, icon="✅")
                elif status == "warning":
                    st.toast(full_message, icon="⚠️")
                elif status == "error":
                    st.toast(full_message, icon="❌")
                else:
                    st.toast(full_message, icon="ℹ️")

                # Mark notification as read
                try:
                    httpx.post(f"{API_BASE}/notifications/{notif['id']}/read", timeout=2)
                except Exception:
                    pass

            # If there was a successful capture, trigger a rerun to update statistics
            if has_new_success:
                st.rerun()
    except Exception as e:
        pass

    # Render placeholder - fragment needs to render something
    st.empty()


def render_live_notification_banner():
    """Render a live notification banner that shows recent captures."""
    try:
        response = httpx.get(
            f"{API_BASE}/notifications",
            params={"limit": 1, "unread_only": False},
            timeout=2
        )
        if response.status_code == 200:
            data = response.json()
            notifications = data.get("notifications", [])
            if notifications:
                notif = notifications[0]
                status = notif.get("status", "info")
                title = notif.get("title", "")
                message = notif.get("message", "")
                timestamp = notif.get("timestamp", "")[:19] if notif.get("timestamp") else ""

                if status == "success":
                    st.success(f"**Latest:** {title} - {message} ({timestamp})")
                elif status == "warning":
                    st.warning(f"**Latest:** {title} - {message} ({timestamp})")
                elif status == "error":
                    st.error(f"**Latest:** {title} - {message} ({timestamp})")
    except Exception:
        pass


def parse_sse_stream(response):
    """Parse Server-Sent Events from response."""
    for line in response.iter_lines():
        if line:
            # Handle both bytes and string responses
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            if line.startswith('data: '):
                data = line[6:]  # Remove 'data: ' prefix
                try:
                    yield json.loads(data)
                except json.JSONDecodeError:
                    continue


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

    # Display any notifications from initial page load
    display_notifications()

    # Auto-refresh fragment for real-time notifications (runs every 2 seconds)
    auto_refresh_notifications()

    st.title("🧠 Local Recall Dashboard")
    st.markdown("*Privacy-preserving local text capture and RAG system*")

    st.markdown("""
    **How it works:** Local Recall streamlines your workflow by capturing text and screenshots directly from any application
    using convenient keyboard shortcuts. Instead of repeatedly copying text or uploading screenshots to your LLM, simply press
    the configured keybind to instantly save content to your local knowledge base. The captured information is automatically
    embedded and indexed, making it immediately searchable through semantic queries. When you ask a question, the RAG system
    retrieves the most relevant context from your captured data and provides AI-powered answers—all while keeping your data
    private and local.
    """)

    # Sidebar for system control and stats
    with st.sidebar:
        st.header("System Control")

        status = get_status()

        if status:
            # Notification toggle
            st.session_state.notifications_enabled = st.checkbox(
                "Show capture notifications",
                value=st.session_state.notifications_enabled,
                help="Display toast notifications when text is captured"
            )

            # Manual refresh button
            if st.button("🔄 Refresh", use_container_width=True, help="Refresh to see latest captures"):
                st.rerun()

            st.divider()

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

            st.divider()

            # Live capture activity indicator
            st.header("Last Capture")
            render_live_notification_banner()

        else:
            st.error("Backend not available")
            st.info("Start the backend with: `python backend/api.py`")

    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search & Query", "📊 Data Browser", "📁 Upload", "⚙️ Settings"])

    with tab1:
        st.header("Semantic Search & RAG")

        query = st.text_input("Enter your query:", placeholder="What are you looking for?")

        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            use_rag = st.checkbox("Use RAG (LLM-powered answers)", value=True)

        with col2:
            num_results = st.slider("Number of results", 1, 10, 5)

        with col3:
            use_streaming = st.checkbox("Stream responses", value=True, help="Display answers as they are generated")

        with col4:
            # Model selection
            model_options = [
                settings.LLM_MODEL,  # Default Ollama model
                "llama3.1:8b",
                "llama3:latest",
                "mistral:latest",
                "gpt-4o-mini",
                "gpt-4o",
                "gpt-3.5-turbo"
            ]
            # Remove duplicates while preserving order
            seen = set()
            unique_models = []
            for model in model_options:
                if model not in seen:
                    seen.add(model)
                    unique_models.append(model)

            selected_model = st.selectbox(
                "Model",
                unique_models,
                index=0,
                help="Select Ollama (local) or OpenAI model"
            )

        if st.button("🔍 Search", type="primary", use_container_width=True):
            if query:
                with st.spinner("Searching..."):
                    try:
                        # Handle RAG with streaming
                        if use_rag and use_streaming:
                            with httpx.stream(
                                "POST",
                                f"{API_BASE}/query/stream",
                                json={"query": query, "model": selected_model, "k": num_results},
                                timeout=120
                            ) as response:
                                if response.status_code == 200:
                                    # Create placeholders for progressive display
                                    answer_placeholder = st.empty()
                                    sources_placeholder = st.empty()

                                    metadata = None
                                    answer_text = ""

                                    # Process streaming events
                                    for event in parse_sse_stream(response):
                                        if event.get("type") == "metadata":
                                            metadata = event
                                        elif event.get("type") == "answer_chunk":
                                            answer_text += event.get("content", "")
                                            # Update answer display progressively
                                            with answer_placeholder.container():
                                                st.subheader("💡 Answer")
                                                st.markdown(f"**{answer_text}**▊")  # Add cursor for streaming effect
                                        elif event.get("type") == "done":
                                            # Final update without cursor
                                            with answer_placeholder.container():
                                                st.subheader("💡 Answer")
                                                st.markdown(f"**{answer_text}**")
                                                if metadata and metadata.get('model'):
                                                    st.caption(f"🤖 Generated using: {metadata['model']}")
                                        elif event.get("type") == "error":
                                            st.error(event.get("content", "Unknown error"))

                                    # Display sources after streaming completes
                                    if metadata:
                                        sources = metadata.get('sources', [])
                                        if sources:
                                            with sources_placeholder.container():
                                                st.divider()
                                                st.subheader(f"📚 Sources ({len(sources)} retrieved)")

                                                for idx, source in enumerate(sources, 1):
                                                    score = source['score']
                                                    if score > 0.8:
                                                        score_color = "🟢"
                                                    elif score > 0.6:
                                                        score_color = "🟡"
                                                    else:
                                                        score_color = "🟠"

                                                    with st.expander(f"{score_color} Source {idx} - Entry #{source['id']} (Relevance: {score:.1%})"):
                                                        entry_data = httpx.get(f"{API_BASE}/data?id={source['id']}").json()
                                                        if entry_data:
                                                            content = entry_data[0]['content']
                                                            st.markdown("**Content:**")
                                                            st.markdown(f"> {content}")

                                                            col1, col2, col3 = st.columns(3)
                                                            with col1:
                                                                st.caption(f"📂 **Source:** {entry_data[0].get('source', 'Unknown')}")
                                                            with col2:
                                                                st.caption(f"🕒 **Time:** {entry_data[0].get('timestamp', 'N/A')[:19] if entry_data[0].get('timestamp') else 'N/A'}")
                                                            with col3:
                                                                st.caption(f"📝 **Length:** {len(content)} chars")
                                else:
                                    st.error(f"Search failed: {response.status_code}")

                        # Handle RAG without streaming
                        elif use_rag:
                            response = httpx.post(
                                f"{API_BASE}/query",
                                json={"query": query, "model": selected_model, "k": num_results},
                                timeout=120
                            )
                            if response.status_code == 200:
                                result = response.json()

                                st.subheader("💡 Answer")
                                st.markdown(f"**{result.get('answer', 'No answer generated')}**")

                                if result.get('model'):
                                    st.caption(f"🤖 Generated using: {result['model']}")

                                sources = result.get('sources', [])
                                if not sources:
                                    st.info("No data found. Capture some text first using Ctrl+Alt+R or upload documents.")
                                else:
                                    st.divider()
                                    st.subheader(f"📚 Sources ({len(sources)} retrieved)")

                                    for idx, source in enumerate(sources, 1):
                                        score = source['score']
                                        if score > 0.8:
                                            score_color = "🟢"
                                        elif score > 0.6:
                                            score_color = "🟡"
                                        else:
                                            score_color = "🟠"

                                        with st.expander(f"{score_color} Source {idx} - Entry #{source['id']} (Relevance: {score:.1%})"):
                                            entry_data = httpx.get(f"{API_BASE}/data?id={source['id']}").json()
                                            if entry_data:
                                                content = entry_data[0]['content']
                                                st.markdown("**Content:**")
                                                st.markdown(f"> {content}")

                                                col1, col2, col3 = st.columns(3)
                                                with col1:
                                                    st.caption(f"📂 **Source:** {entry_data[0].get('source', 'Unknown')}")
                                                with col2:
                                                    st.caption(f"🕒 **Time:** {entry_data[0].get('timestamp', 'N/A')[:19] if entry_data[0].get('timestamp') else 'N/A'}")
                                                with col3:
                                                    st.caption(f"📝 **Length:** {len(content)} chars")
                            else:
                                st.error(f"Search failed: {response.status_code}")

                        # Handle semantic search only
                        else:
                            response = httpx.post(
                                f"{API_BASE}/query",
                                json={"query": query, "k": num_results},
                                timeout=60
                            )
                            if response.status_code == 200:
                                result = response.json()
                                results = result.get('results', [])
                                if not results:
                                    st.info("No results found. Capture some text first using Ctrl+Alt+R or upload documents.")
                                else:
                                    st.subheader(f"🔍 Found {len(results)} Results")

                                    for idx, res in enumerate(results, 1):
                                        score = res['score']
                                        if score > 0.8:
                                            score_color = "🟢"
                                        elif score > 0.6:
                                            score_color = "🟡"
                                        else:
                                            score_color = "🟠"

                                        with st.expander(f"{score_color} Result {idx} - Entry #{res['id']} (Relevance: {score:.1%})"):
                                            st.markdown("**Content:**")
                                            st.markdown(f"> {res['text']}")

                                            col1, col2, col3 = st.columns(3)
                                            with col1:
                                                st.caption(f"📂 **Source:** {res.get('source', 'Unknown')}")
                                            with col2:
                                                st.caption(f"🕒 **Time:** {res.get('timestamp', 'N/A')[:19] if res.get('timestamp') else 'N/A'}")
                                            with col3:
                                                st.caption(f"📝 **Length:** {len(res['text'])} chars")
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
            filter_source = st.selectbox(
                "Filter by source:",
                options=["All", "clipboard", "screenshot"],
                index=0,
                help="Filter entries by capture method"
            )
        with col2:
            filter_tag = st.text_input("Filter by tag:", placeholder="e.g., important")
        with col3:
            limit = st.number_input("Limit", min_value=10, max_value=500, value=50)

        if st.button("Load Entries", use_container_width=True):
            try:
                params = {"limit": limit}
                if filter_source and filter_source != "All":
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
                temp_path = None
                try:
                    # Save uploaded file temporarily
                    temp_path = Path(f"./temp_{uploaded_file.name}")
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Parse document
                    content = document_parser.parse_file(str(temp_path))

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
                    elif content == "":
                        # Empty string means parsing worked but no text found
                        file_ext = uploaded_file.name.split('.')[-1].lower()
                        if file_ext == 'pdf':
                            st.error("No text could be extracted from this PDF. It may be scanned/image-based. Try using a PDF with selectable text.")
                        else:
                            st.error("The document appears to be empty or contains no extractable text.")
                    else:
                        # None means parsing failed
                        st.error("Failed to extract text from document. The file format may be unsupported or corrupted.")

                except Exception as e:
                    st.error(f"Error processing document: {e}")
                finally:
                    # Clean up temp file
                    if temp_path and temp_path.exists():
                        try:
                            temp_path.unlink()
                        except Exception:
                            pass

    with tab4:
        st.header("Settings")

        st.subheader("Keybinds")
        st.info("Keybinds allow you to quickly capture text without leaving your workflow")

        # Platform-specific keybind tabs
        keybind_tab1, keybind_tab2 = st.tabs(["🍎 macOS", "🪟 Windows/Linux"])

        try:
            keybinds_response = httpx.get(f"{API_BASE}/keybinds", timeout=5)
            if keybinds_response.status_code == 200:
                keybinds = keybinds_response.json()

                # Separate keybinds by platform
                mac_keybinds = [kb for kb in keybinds if "<cmd>" in kb['key_sequence']]
                windows_linux_keybinds = [kb for kb in keybinds if "<ctrl>" in kb['key_sequence'] and "<cmd>" not in kb['key_sequence']]

                with keybind_tab1:
                    st.markdown("**macOS Keybinds**")
                    if mac_keybinds:
                        for kb in mac_keybinds:
                            action_name = "Capture Selected Text" if kb['action'] == "capture_selected" else "Capture Screenshot"
                            st.code(f"{action_name}: {kb['key_sequence']}")
                    else:
                        st.warning("No macOS keybinds configured")

                    st.markdown("**Add New macOS Keybind**")
                    col1, col2 = st.columns(2)
                    with col1:
                        action_mac = st.selectbox("Action", ["capture_selected", "capture_screenshot"], key="mac_action")
                    with col2:
                        key_seq_mac = st.text_input("Key Sequence", placeholder="<cmd>+<ctrl>+r", key="mac_key")

                    if st.button("Add macOS Keybind"):
                        if key_seq_mac:
                            endpoint = "/keybind/selected" if action_mac == "capture_selected" else "/keybind/screenshot"
                            response = httpx.post(
                                f"{API_BASE}{endpoint}",
                                json={"key_sequence": key_seq_mac}
                            )
                            if response.status_code == 200:
                                st.success(f"Keybind added: {key_seq_mac} -> {action_mac}")
                                st.info("Note: Restart the capture service for new keybinds to take effect")
                                st.rerun()
                            else:
                                st.error(f"Failed to add keybind: {response.text}")

                with keybind_tab2:
                    st.markdown("**Windows/Linux Keybinds**")
                    if windows_linux_keybinds:
                        for kb in windows_linux_keybinds:
                            action_name = "Capture Selected Text" if kb['action'] == "capture_selected" else "Capture Screenshot"
                            st.code(f"{action_name}: {kb['key_sequence']}")
                    else:
                        st.warning("No Windows/Linux keybinds configured")

                    st.markdown("**Add New Windows/Linux Keybind**")
                    col1, col2 = st.columns(2)
                    with col1:
                        action_win = st.selectbox("Action", ["capture_selected", "capture_screenshot"], key="win_action")
                    with col2:
                        key_seq_win = st.text_input("Key Sequence", placeholder="<ctrl>+<alt>+r", key="win_key")

                    if st.button("Add Windows/Linux Keybind"):
                        if key_seq_win:
                            endpoint = "/keybind/selected" if action_win == "capture_selected" else "/keybind/screenshot"
                            response = httpx.post(
                                f"{API_BASE}{endpoint}",
                                json={"key_sequence": key_seq_win}
                            )
                            if response.status_code == 200:
                                st.success(f"Keybind added: {key_seq_win} -> {action_win}")
                                st.info("Note: Restart the capture service for new keybinds to take effect")
                                st.rerun()
                            else:
                                st.error(f"Failed to add keybind: {response.text}")
        except Exception as e:
            st.error(f"Error loading keybinds: {e}")

        st.divider()

        st.subheader("Configuration")
        st.code(f"Embedding Model: {settings.EMBEDDING_MODEL}")
        st.code(f"LLM Model (Default): {settings.LLM_MODEL}")
        st.code(f"Database: {settings.DATABASE_PATH}")
        st.code(f"FAISS Index: {settings.FAISS_INDEX_PATH}")

        st.divider()

        st.subheader("OpenAI API Configuration")
        st.info("To use OpenAI models (gpt-4o, gpt-4o-mini, etc.), set your OPENAI_API_KEY environment variable.")

        if settings.OPENAI_API_KEY:
            st.success("✅ OpenAI API key is configured")
            st.caption(f"Using model: {settings.OPENAI_MODEL}")
        else:
            st.warning("⚠️ OpenAI API key not configured")
            st.caption("Set OPENAI_API_KEY in your .env file or environment variables to enable OpenAI models")
            st.code('OPENAI_API_KEY="sk-..."', language="bash")

        st.divider()

        st.subheader("Recent Capture Activity")
        st.caption("Shows recent capture events from the background service")

        try:
            notif_response = httpx.get(
                f"{API_BASE}/notifications",
                params={"limit": 10},
                timeout=5
            )
            if notif_response.status_code == 200:
                notifications = notif_response.json().get("notifications", [])

                if notifications:
                    for notif in notifications:
                        status = notif.get("status", "info")
                        title = notif.get("title", "")
                        message = notif.get("message", "")
                        timestamp = notif.get("timestamp", "")[:19] if notif.get("timestamp") else ""

                        if status == "success":
                            icon = "✅"
                        elif status == "warning":
                            icon = "⚠️"
                        elif status == "error":
                            icon = "❌"
                        else:
                            icon = "ℹ️"

                        with st.expander(f"{icon} {title} ({timestamp})"):
                            st.markdown(message)
                else:
                    st.info("No recent capture activity. Use Ctrl+Alt+R (text) or Ctrl+Alt+T (screenshot) to capture.")

                if notifications and st.button("Clear All Notifications"):
                    httpx.post(f"{API_BASE}/notifications/read-all", timeout=5)
                    st.rerun()
        except Exception as e:
            st.warning(f"Could not load notifications: {e}")


if __name__ == "__main__":
    main()
