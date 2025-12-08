# CS 146S: Local Recall

Privacy-preserving local text capture and RAG system for knowledge workers.

## Overview

Local Recall is a lightweight background tool that automatically captures and consolidates your digital text data, enabling semantic search and RAG-based querying using local LLMs. All data stays on your device for complete privacy and control.

## Features

- **Text Capture**: Capture text via keybinds (selected text, screenshots)
- **Document Upload**: Support for TXT, PDF, and DOCX files
- **Semantic Search**: Find relevant information across all your captured data
- **RAG-Based Queries**: Get contextual answers using local LLMs (via Ollama)
- **Privacy-First**: All data stored locally, never leaves your device
- **Background Operation**: Runs silently with minimal impact

## Prerequisites

1. **Python 3.9+**
2. **Ollama** - For local LLM and embeddings
   - Install from: https://ollama.ai
   - Pull required models:
     ```bash
     ollama pull nomic-embed-text
     ollama pull llama3.1:8b
     ```
3. **Tesseract OCR** (for screenshot text capture)
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Mac: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

## Quick Start

### Windows

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd local-recall
   ```

2. Run the startup script:
   ```bash
   start.bat
   ```

### Linux/Mac

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd local-recall
   ```

2. Make the startup script executable and run:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

### Manual Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

4. Run components:
   ```bash
   # Run all components
   python main.py all

   # Or run individually
   python main.py backend   # FastAPI backend on port 8000
   python main.py frontend  # Streamlit dashboard on port 8501
   python main.py capture   # Background capture service
   ```

## Usage

### Default Keybinds

#### Windows/Linux
- **Ctrl+Alt+R**: Capture selected text (copies from clipboard)
- **Ctrl+Alt+T**: Capture screenshot text (OCR)

#### macOS
- **Cmd+Ctrl+R**: Capture selected text (copies from clipboard)
- **Cmd+Ctrl+T**: Capture screenshot text (OCR)

**Note for macOS users**: Due to system accessibility restrictions, you need to manually copy text with **Cmd+C** first, then press **Cmd+Ctrl+R** to capture it.

### Dashboard

Access the dashboard at: http://localhost:8501

Features:
- **Search & Query**: Semantic search and RAG-based Q&A
- **Data Browser**: View and manage captured entries
- **Upload**: Add documents (TXT, PDF, DOCX)
- **Settings**: Configure keybinds and view system stats

### API

Backend API available at: http://localhost:8000

Docs: http://localhost:8000/docs

## Architecture

```
┌─────────────────┐
│  User's Device  │
│                 │
│  ┌───────────┐  │
│  │ Keybind   │  │
│  │ Listener  │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │  SQLite   │◄─┼──► FastAPI Backend (Port 8000)
│  │  Database │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │   FAISS   │  │
│  │  Vectors  │  │
│  └─────┬─────┘  │
│        │        │
│  ┌─────▼─────┐  │
│  │  Ollama   │◄─┼──► Streamlit Dashboard (Port 8501)
│  │  (Local)  │  │
│  └───────────┘  │
└─────────────────┘
```

## Project Structure

```
local-recall/
├── backend/           # FastAPI backend
│   └── api.py
├── capture/           # Text capture service
│   ├── keybind_listener.py
│   ├── text_capture.py
│   └── capture_service.py
├── database/          # SQLite database
│   ├── models.py
│   └── db.py
├── embeddings/        # Embedding generation
│   ├── ollama_embeddings.py
│   └── pipeline.py
├── frontend/          # Streamlit dashboard
│   └── app.py
├── rag/              # RAG query engine
│   └── query_engine.py
├── utils/            # Utilities
│   └── document_parser.py
├── vector_store/     # FAISS integration
│   └── faiss_store.py
├── config.py         # Configuration
├── main.py           # Entry point
└── requirements.txt  # Dependencies
```

## Configuration

Edit `.env` file to customize:

```env
DATABASE_PATH=./data/local_recall.db
FAISS_INDEX_PATH=./data/faiss_index
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
LLM_MODEL=llama3.1:8b
BACKEND_PORT=8000
FRONTEND_PORT=8501
LOG_LEVEL=INFO
```

## Development

### Running Components Separately

```bash
# Backend only
python main.py backend

# Frontend only
python main.py frontend

# Capture service only
python main.py capture

# Initialize system (create directories, default keybinds)
python main.py init
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests (to be implemented)
pytest
```

## Privacy & Security

- **Local-Only**: All data stored locally in SQLite database
- **No Cloud**: No data transmitted to external services
- **User Control**: Full control over what's captured and stored
- **Opt-In/Out**: Easy start/stop controls for capture

## Troubleshooting

### Ollama Connection Error

Ensure Ollama is running:
```bash
ollama serve
```

And models are pulled:
```bash
ollama pull nomic-embed-text
ollama pull llama3.1:8b
```

### Tesseract Not Found

Install Tesseract OCR and add to PATH:
- Windows: Add installation directory to system PATH
- Verify: `tesseract --version`

### Port Already in Use

Change ports in `.env`:
```env
BACKEND_PORT=8001
FRONTEND_PORT=8502
```

## Roadmap

- [ ] Cloud sync option (optional, encrypted)
- [ ] Browser extension for web capture
- [ ] Advanced filtering and tagging
- [ ] Export capabilities
- [ ] Mobile app integration
- [ ] Multi-modal support (images, audio)

## License

MIT License

## Authors

Advit Deepak, Sriram Varun Vobilisetty
CS146S - Autumn 2025
