"""Streamlit dashboard for Local Recall."""
import streamlit as st
import httpx
from datetime import datetime
from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).parent.parent))

from config import settings
from utils import document_parser
from database import db

API_BASE = f"http://localhost:{settings.BACKEND_PORT}"


def apply_custom_css():
    """Apply custom CSS for modern design."""
    st.markdown("""
    <style>
        /* Import modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global styles */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Main container */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 2rem 1rem;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
            box-shadow: 4px 0 12px rgba(0,0,0,0.1);
        }

        [data-testid="stSidebar"] * {
            color: white !important;
        }

        /* Header styling */
        h1 {
            font-weight: 700;
            font-size: 2.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.5rem;
        }

        h2 {
            font-weight: 600;
            font-size: 1.75rem;
            color: #2d3748;
            margin-top: 1.5rem;
        }

        h3 {
            font-weight: 600;
            font-size: 1.25rem;
            color: #4a5568;
        }

        /* Card styling */
        .card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.07);
            margin-bottom: 1.5rem;
            border: 1px solid #e2e8f0;
            transition: all 0.3s ease;
        }

        .card:hover {
            box-shadow: 0 10px 20px rgba(0,0,0,0.12);
            transform: translateY(-2px);
        }

        /* Metric cards */
        [data-testid="stMetric"] {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        }

        /* Button styling */
        .stButton button {
            border-radius: 8px;
            font-weight: 500;
            padding: 0.6rem 1.5rem;
            transition: all 0.3s ease;
            border: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        /* Primary button */
        .stButton button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        /* Input styling */
        .stTextInput input, .stTextArea textarea, .stSelectbox select {
            border-radius: 8px;
            border: 2px solid #e2e8f0;
            padding: 0.75rem;
            transition: all 0.3s ease;
        }

        .stTextInput input:focus, .stTextArea textarea:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: white;
            border-radius: 12px;
            padding: 0.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            background: transparent;
            border: none;
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
        }

        /* Expander styling */
        .streamlit-expanderHeader {
            background: white;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            font-weight: 500;
        }

        /* Success/Warning/Error boxes */
        .stSuccess, .stWarning, .stError, .stInfo {
            border-radius: 8px;
            padding: 1rem;
            border-left: 4px solid;
        }

        /* Divider */
        hr {
            margin: 2rem 0;
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        }

        /* Score indicators */
        .score-high {
            color: #48bb78;
            font-weight: 600;
        }

        .score-medium {
            color: #ed8936;
            font-weight: 600;
        }

        .score-low {
            color: #f56565;
            font-weight: 600;
        }

        /* Status badge */
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 600;
            margin-right: 0.5rem;
        }

        .status-active {
            background: #c6f6d5;
            color: #22543d;
        }

        .status-paused {
            background: #feebc8;
            color: #7c2d12;
        }

        /* Smooth transitions */
        * {
            transition: background-color 0.3s ease, transform 0.3s ease;
        }
    </style>
    """, unsafe_allow_html=True)


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


def render_status_card(is_capturing, db_stats, vs_stats):
    """Render a modern status overview card."""
    status_badge = "status-active" if is_capturing else "status-paused"
    status_text = "ACTIVE" if is_capturing else "PAUSED"
    status_icon = "▶" if is_capturing else "⏸"

    st.markdown(f"""
    <div class="card">
        <h3 style="margin-top: 0;">System Status</h3>
        <span class="status-badge {status_badge}">{status_icon} {status_text}</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Entries", db_stats.get('total_entries', 0), delta=None)
    with col2:
        st.metric("Embedded", db_stats.get('embedded_entries', 0), delta=None)
    with col3:
        st.metric("Vectors", vs_stats.get('total_vectors', 0), delta=None)


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Local Recall",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    apply_custom_css()
    init_session_state()
    display_notifications()
    auto_refresh_notifications()

    st.title("Local Recall")
    st.markdown("### Your private AI-powered knowledge base")

    st.markdown("""
    <div class="card">
        <p style="font-size: 1rem; color: #4a5568; line-height: 1.6; margin: 0;">
        Capture text and screenshots with keyboard shortcuts, search semantically across your data,
        and get AI-powered answers—all while keeping your data completely private and local.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## Control Panel")

        status = get_status()

        if status:
            st.session_state.notifications_enabled = st.checkbox(
                "Live Notifications",
                value=st.session_state.notifications_enabled,
                help="Show real-time capture notifications"
            )

            if st.button("🔄 Refresh Dashboard", use_container_width=True):
                st.rerun()

            st.divider()

            is_capturing = status.get('capturing', False)
            db_stats = status.get('database', {})
            vs_stats = status.get('vector_store', {})

            st.markdown("### Quick Actions")

            if is_capturing:
                if st.button("⏸ Stop Capture", use_container_width=True, type="secondary"):
                    stop_capture()
            else:
                if st.button("▶ Start Capture", use_container_width=True, type="primary"):
                    start_capture()

            st.divider()

            st.markdown("### Analytics")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Entries", db_stats.get('total_entries', 0))
                st.metric("Vectors", vs_stats.get('total_vectors', 0))
            with col2:
                st.metric("Embedded", db_stats.get('embedded_entries', 0))
                st.metric("Pending", db_stats.get('pending_embeddings', 0))

            st.divider()
            st.markdown("### Keyboard Shortcuts")
            st.markdown("""
            **Windows/Linux:**
            - `Ctrl+Alt+R` - Capture text
            - `Ctrl+Alt+T` - Screenshot OCR

            **macOS:**
            - `Cmd+Ctrl+R` - Capture text
            - `Cmd+Ctrl+T` - Screenshot OCR
            """)

        else:
            st.error("Backend Offline")
            st.caption("Start with: `python main.py all`")

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Search", "📊 Browse", "📁 Upload", "⚙️ Settings"])

    with tab1:
        st.markdown("### Search Your Knowledge Base")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        query = st.text_input(
            "What would you like to know?",
            placeholder="Ask a question or search for information...",
            label_visibility="collapsed"
        )

        with st.expander("⚙ Search Options", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                use_rag = st.checkbox("AI-Powered Answers", value=True, help="Use LLM for contextual answers")
                use_streaming = st.checkbox("Stream Response", value=True, help="Show answer as it generates")
            with col2:
                num_results = st.slider("Context Sources", 1, 10, 5, help="Number of relevant sources to retrieve")

                model_options = [
                    settings.LLM_MODEL,
                    "llama3.1:8b",
                    "llama3:latest",
                    "mistral:latest",
                    "gpt-4o-mini",
                    "gpt-4o",
                    "gpt-3.5-turbo"
                ]
                seen = set()
                unique_models = []
                for model in model_options:
                    if model not in seen:
                        seen.add(model)
                        unique_models.append(model)

                selected_model = st.selectbox(
                    "AI Model",
                    unique_models,
                    index=0,
                    help="Select LLM model"
                )

        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("🔍 Search", type="primary", use_container_width=True, disabled=not query):
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

                                    if metadata:
                                        sources = metadata.get('sources', [])
                                        if sources:
                                            with sources_placeholder.container():
                                                st.markdown("---")
                                                st.markdown(f"#### 📚 Sources ({len(sources)} found)")

                                                for idx, source in enumerate(sources, 1):
                                                    score = source['score']
                                                    if score > 0.8:
                                                        score_color = "🟢"
                                                        score_class = "score-high"
                                                    elif score > 0.6:
                                                        score_color = "🟡"
                                                        score_class = "score-medium"
                                                    else:
                                                        score_color = "🟠"
                                                        score_class = "score-low"

                                                    with st.expander(f"{score_color} Source {idx} • Relevance: {score:.1%}", expanded=(idx==1)):
                                                        entry_data = httpx.get(f"{API_BASE}/data?id={source['id']}").json()
                                                        if entry_data:
                                                            content = entry_data[0]['content']
                                                            st.markdown(f"> {content}")

                                                            col1, col2, col3 = st.columns(3)
                                                            with col1:
                                                                st.caption(f"📂 {entry_data[0].get('source', 'Unknown')}")
                                                            with col2:
                                                                st.caption(f"🕒 {entry_data[0].get('timestamp', 'N/A')[:19] if entry_data[0].get('timestamp') else 'N/A'}")
                                                            with col3:
                                                                st.caption(f"📝 {len(content)} chars")
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
        st.markdown("### Browse Your Data")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            filter_source = st.selectbox(
                "Source",
                options=["All", "clipboard", "screenshot"],
                index=0
            )
        with col2:
            filter_tag = st.text_input(
                "Tag",
                placeholder="Filter by tag..."
            )
        with col3:
            limit = st.number_input("Limit", min_value=10, max_value=500, value=50, step=10)

        if st.button("🔄 Load Entries", use_container_width=True, type="primary"):
            try:
                params = {"limit": limit}
                if filter_source and filter_source != "All":
                    params["source"] = filter_source
                if filter_tag:
                    params["tag"] = filter_tag

                response = httpx.get(f"{API_BASE}/data", params=params, timeout=10)

                if response.status_code == 200:
                    entries = response.json()
                    st.success(f"Found {len(entries)} entries")

                    if not entries:
                        st.info("No entries found. Start capturing with Ctrl+Alt+R or upload documents.")
                    else:
                        for entry in entries:
                            timestamp = entry.get('timestamp', '')[:19] if entry.get('timestamp') else 'N/A'
                            method_icon = "📋" if entry.get('capture_method') == "selected" else "📸" if entry.get('capture_method') == "screenshot" else "📄"

                            with st.expander(f"{method_icon} Entry #{entry['id']} • {entry.get('source', 'Unknown')} • {timestamp}"):
                                st.markdown(f"**Content:**")
                                st.text_area("", entry['content'], height=120, key=f"entry_{entry['id']}", label_visibility="collapsed")

                                col_a, col_b = st.columns([3, 1])
                                with col_a:
                                    tags = entry.get('tags', [])
                                    if tags:
                                        st.caption(f"🏷 Tags: {', '.join(tags)}")
                                    st.caption(f"Method: {entry.get('capture_method', 'Unknown')}")
                                with col_b:
                                    if st.button("🗑 Delete", key=f"delete_{entry['id']}", type="secondary"):
                                        delete_response = httpx.delete(f"{API_BASE}/data/{entry['id']}")
                                        if delete_response.status_code == 200:
                                            st.success("Deleted")
                                            st.rerun()
                else:
                    st.error("Failed to load entries")
            except Exception as e:
                st.error(f"Error: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("### Upload Documents")

        st.markdown("""
        <div class="card">
            <p style="color: #4a5568; margin: 0;">
            Upload TXT, PDF, or DOCX files to add them to your knowledge base. Documents will be automatically embedded and indexed for semantic search.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'pdf', 'docx'],
            help="Supported formats: TXT, PDF, DOCX"
        )

        if uploaded_file:
            st.info(f"Selected: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")

            tags_input = st.text_input("Add Tags (optional)", placeholder="work, research, important...")

            if st.button("📤 Upload & Process", type="primary", use_container_width=True):
                with st.spinner("Processing document..."):
                    temp_path = None
                    try:
                        temp_path = Path(f"./temp_{uploaded_file.name}")
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())

                        content = document_parser.parse_file(str(temp_path))

                        if content:
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
                                st.info(f"Extracted {len(content):,} characters")
                            else:
                                st.error("Failed to save to database")
                        elif content == "":
                            file_ext = uploaded_file.name.split('.')[-1].lower()
                            if file_ext == 'pdf':
                                st.error("No text found. PDF may be scanned/image-based.")
                            else:
                                st.error("Document is empty or contains no text.")
                        else:
                            st.error("Failed to extract text. File may be corrupted.")

                    except Exception as e:
                        st.error(f"Error: {e}")
                    finally:
                        if temp_path and temp_path.exists():
                            try:
                                temp_path.unlink()
                            except Exception:
                                pass

        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown("### Settings & Configuration")

        st.markdown("#### System Configuration")
        st.markdown('<div class="card">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Embedding Model**")
            st.code(settings.EMBEDDING_MODEL)
            st.markdown("**LLM Model**")
            st.code(settings.LLM_MODEL)
        with col2:
            st.markdown("**Database Path**")
            st.caption(settings.DATABASE_PATH)
            st.markdown("**Vector Index**")
            st.caption(settings.FAISS_INDEX_PATH)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("#### OpenAI Configuration")
        st.markdown('<div class="card">', unsafe_allow_html=True)

        if settings.OPENAI_API_KEY:
            st.success("OpenAI API key is configured")
            st.caption(f"Default model: {settings.OPENAI_MODEL}")
        else:
            st.warning("OpenAI API key not configured")
            st.caption("Set OPENAI_API_KEY in .env file to enable GPT models")
            st.code('OPENAI_API_KEY="sk-..."', language="bash")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("#### Keyboard Shortcuts")
        st.markdown('<div class="card">', unsafe_allow_html=True)

        keybind_tab1, keybind_tab2 = st.tabs(["🍎 macOS", "🪟 Windows/Linux"])

        try:
            keybinds_response = httpx.get(f"{API_BASE}/keybinds", timeout=5)
            if keybinds_response.status_code == 200:
                keybinds = keybinds_response.json()

                mac_keybinds = [kb for kb in keybinds if "<cmd>" in kb['key_sequence']]
                windows_linux_keybinds = [kb for kb in keybinds if "<ctrl>" in kb['key_sequence'] and "<cmd>" not in kb['key_sequence']]

                with keybind_tab1:
                    st.markdown("**Active Keybinds**")
                    if mac_keybinds:
                        for kb in mac_keybinds:
                            action_name = "Capture Text" if kb['action'] == "capture_selected" else "Screenshot OCR"
                            st.code(f"{action_name}: {kb['key_sequence']}")
                    else:
                        st.info("No macOS keybinds configured")

                    with st.expander("➕ Add New Keybind"):
                        col1, col2 = st.columns(2)
                        with col1:
                            action_mac = st.selectbox("Action", ["capture_selected", "capture_screenshot"], key="mac_action")
                        with col2:
                            key_seq_mac = st.text_input("Sequence", placeholder="<cmd>+<ctrl>+r", key="mac_key")

                        if st.button("Add Keybind", key="add_mac"):
                            if key_seq_mac:
                                endpoint = "/keybind/selected" if action_mac == "capture_selected" else "/keybind/screenshot"
                                response = httpx.post(f"{API_BASE}{endpoint}", json={"key_sequence": key_seq_mac})
                                if response.status_code == 200:
                                    st.success("Keybind added. Restart capture service.")
                                    st.rerun()
                                else:
                                    st.error("Failed to add keybind")

                with keybind_tab2:
                    st.markdown("**Active Keybinds**")
                    if windows_linux_keybinds:
                        for kb in windows_linux_keybinds:
                            action_name = "Capture Text" if kb['action'] == "capture_selected" else "Screenshot OCR"
                            st.code(f"{action_name}: {kb['key_sequence']}")
                    else:
                        st.info("No Windows/Linux keybinds configured")

                    with st.expander("➕ Add New Keybind"):
                        col1, col2 = st.columns(2)
                        with col1:
                            action_win = st.selectbox("Action", ["capture_selected", "capture_screenshot"], key="win_action")
                        with col2:
                            key_seq_win = st.text_input("Sequence", placeholder="<ctrl>+<alt>+r", key="win_key")

                        if st.button("Add Keybind", key="add_win"):
                            if key_seq_win:
                                endpoint = "/keybind/selected" if action_win == "capture_selected" else "/keybind/screenshot"
                                response = httpx.post(f"{API_BASE}{endpoint}", json={"key_sequence": key_seq_win})
                                if response.status_code == 200:
                                    st.success("Keybind added. Restart capture service.")
                                    st.rerun()
                                else:
                                    st.error("Failed to add keybind")
        except Exception as e:
            st.error(f"Error loading keybinds: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("#### Recent Activity")
        st.markdown('<div class="card">', unsafe_allow_html=True)

        try:
            notif_response = httpx.get(f"{API_BASE}/notifications", params={"limit": 5}, timeout=5)
            if notif_response.status_code == 200:
                notifications = notif_response.json().get("notifications", [])

                if notifications:
                    for notif in notifications:
                        status = notif.get("status", "info")
                        title = notif.get("title", "")
                        message = notif.get("message", "")
                        timestamp = notif.get("timestamp", "")[:19] if notif.get("timestamp") else ""

                        icon = {"success": "✅", "warning": "⚠️", "error": "❌"}.get(status, "ℹ️")

                        with st.expander(f"{icon} {title} • {timestamp}"):
                            st.markdown(message)

                    if st.button("Clear Notifications"):
                        httpx.post(f"{API_BASE}/notifications/read-all", timeout=5)
                        st.rerun()
                else:
                    st.info("No recent activity")
        except Exception as e:
            st.caption(f"Could not load activity: {e}")

        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
