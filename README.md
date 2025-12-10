# Local Recall

Privacy-preserving local text capture and RAG system for knowledge workers.

## Overview

Local Recall is a lightweight background tool that automatically captures and consolidates your digital text data, enabling semantic search and RAG-based querying using local LLMs. All data stays on your device for complete privacy and control.

## Features

- **Text Capture**: Capture text via keybinds (selected text, screenshots with OCR)
- **Document Upload**: Support for TXT, PDF, and DOCX files with drag-and-drop
- **Semantic Search**: Find relevant information across all your captured data using vector embeddings
- **RAG-Based Queries**: Get contextual answers using local LLMs (Ollama) or OpenAI
- **Modern Web UI**: Beautiful Next.js 14 dashboard with dark mode and real-time updates
- **Privacy-First**: All data stored locally in SQLite, never leaves your device
- **Background Operation**: Runs silently with minimal system impact

## Prerequisites

### Backend Requirements

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

### Frontend Requirements

1. **Node.js 18+** and npm
2. Modern web browser (Chrome, Firefox, Safari, Edge)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/AdvitDeepak/local-recall
   cd local-recall
   ```

2. **Backend Setup** (Python):
   
   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   ```
   
   **Linux/Mac:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```

3. **Frontend Setup** (Next.js):
   ```bash
   cd frontend-nextjs
   npm install
   cd ..
   ```

4. **Start the Application**:
   
   **Option A - Start All Components (Recommended):**
   ```bash
   # Backend + Capture Service
   python main.py all
   
   # In a new terminal - Frontend
   cd frontend-nextjs
   npm run dev
   ```
   
   **Option B - Start Components Individually:**
   ```bash
   # Terminal 1: Backend API
   python main.py backend
   
   # Terminal 2: Capture Service
   python main.py capture
   
   # Terminal 3: Frontend
   cd frontend-nextjs
   npm run dev
   ```

5. **Access the Application**:
   - Frontend Dashboard: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Tech Stack

### Backend
- **Framework**: FastAPI (async REST API)
- **Database**: SQLite with SQLAlchemy ORM
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: Ollama (nomic-embed-text)
- **LLM**: Ollama (llama3.1:8b) or OpenAI
- **Document Processing**: PyMuPDF, python-docx, pytesseract
- **System Integration**: pynput (keybinds), pyperclip (clipboard), mss (screenshots)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **State Management**: Zustand
- **Forms**: react-hook-form + zod
- **Markdown Rendering**: react-markdown

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

Access the Next.js dashboard at: http://localhost:3000

**Features:**
- **Search & Query Tab**: 
  - AI-powered semantic search with relevance scoring
  - RAG-based Q&A with streaming responses
  - Support for both Ollama (local) and OpenAI models
  - Source attribution with expandable context
  
- **Data Browser Tab**: 
  - View all captured entries with timestamps
  - Filter by source, tags, and limit
  - Expandable text preview
  - Delete entries with confirmation
  
- **Upload Tab**: 
  - Drag-and-drop file upload
  - Support for TXT, PDF, DOCX formats
  - Tag-based organization
  - Real-time upload progress
  
- **Settings Tab**: 
  - Platform-specific keybind display
  - System statistics and configuration
  - OpenAI integration status

### API

Backend API available at: http://localhost:8000

Interactive API documentation: http://localhost:8000/docs

**Key Endpoints:**
- `GET /stats` - System statistics
- `GET /data` - Retrieve captured entries
- `POST /query` - RAG query
- `POST /query/stream` - Streaming RAG query (SSE)
- `GET /search` - Semantic search
- `POST /upload` - Upload documents
- `DELETE /data/{id}` - Delete entry

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User's Device                      │
│                                                      │
│  ┌──────────────┐                                   │
│  │   Keybind    │  Captures text/screenshots        │
│  │   Listener   │  (Ctrl+Alt+R / Ctrl+Alt+T)        │
│  └──────┬───────┘                                   │
│         │                                            │
│         ▼                                            │
│  ┌──────────────┐         ┌────────────────┐       │
│  │   SQLite     │◄────────┤  FastAPI       │       │
│  │   Database   │         │  Backend       │       │
│  │              │         │  (Port 8000)   │       │
│  └──────┬───────┘         └────────┬───────┘       │
│         │                          │                │
│         ▼                          │                │
│  ┌──────────────┐                 │                │
│  │    FAISS     │  Vector Search  │                │
│  │  Index Store │◄────────────────┘                │
│  └──────┬───────┘                                   │
│         │                                            │
│         ▼                                            │
│  ┌──────────────┐         ┌────────────────┐       │
│  │   Ollama     │◄────────┤   Next.js      │       │
│  │   (Local)    │  LLM    │   Frontend     │       │
│  │  llama3.1:8b │  Calls  │  (Port 3000)   │       │
│  │ nomic-embed  │         │                │       │
│  └──────────────┘         └────────────────┘       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Data Flow:**
1. User captures text via keybinds → Stored in SQLite
2. Background pipeline generates embeddings → Stored in FAISS
3. User queries via Next.js UI → FastAPI backend
4. Backend retrieves relevant context from FAISS → Sends to Ollama
5. Ollama generates response → Streamed back to UI

## Project Structure

```
local-recall/
├── backend/                    # FastAPI backend
│   └── api.py                 # REST API endpoints
├── capture/                    # Text capture service
│   ├── keybind_listener.py    # Global keybind monitoring
│   ├── text_capture.py        # Text/OCR capture logic
│   └── capture_service.py     # Background service
├── database/                   # SQLite database
│   ├── models.py              # SQLAlchemy models
│   └── db.py                  # Database operations
├── embeddings/                 # Embedding generation
│   ├── ollama_embeddings.py   # Ollama embedding client
│   └── pipeline.py            # Background embedding pipeline
├── frontend-nextjs/            # Next.js 14 frontend
│   ├── app/                   # Next.js app directory
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Main page
│   │   └── globals.css        # Global styles
│   ├── components/            # React components
│   │   ├── layout/            # Sidebar, header
│   │   ├── tabs/              # Tab components
│   │   └── ui/                # shadcn/ui components
│   ├── lib/                   # Utilities
│   │   ├── api.ts             # API client
│   │   ├── types.ts           # TypeScript types
│   │   └── hooks/             # Custom hooks
│   ├── package.json           # Node dependencies
│   └── tailwind.config.ts     # Tailwind configuration
├── rag/                        # RAG query engine
│   └── query_engine.py        # Context retrieval + LLM
├── utils/                      # Utilities
│   └── document_parser.py     # PDF/DOCX/TXT parsing
├── vector_store/               # FAISS integration
│   └── faiss_store.py         # Vector similarity search
├── config.py                   # Configuration management
├── main.py                     # Python entry point
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
└── README.md                   # This file
```

## Configuration

### Backend Configuration

Edit `.env` file in the root directory:

```env
# Database & Storage
DATABASE_PATH=./data/local_recall.db
FAISS_INDEX_PATH=./data/faiss_index

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
LLM_MODEL=llama3.1:8b

# Server Ports
BACKEND_PORT=8000
FRONTEND_PORT=8501  # Legacy Streamlit port (not used)

# Logging
LOG_LEVEL=INFO
```

### Frontend Configuration

The Next.js frontend is pre-configured to connect to `http://localhost:8000`. To customize, create `frontend-nextjs/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### OpenAI Integration (Optional)

To use OpenAI models instead of Ollama, add to your `.env`:

```env
OPENAI_API_KEY=your_api_key_here
```

Then select OpenAI models in the frontend Settings tab.

## Development

### Running Components Separately

**Backend API:**
```bash
python main.py backend
# Runs on http://localhost:8000
```

**Capture Service:**
```bash
python main.py capture
# Runs in background, monitors keybinds
```

**Frontend (Next.js):**
```bash
cd frontend-nextjs
npm run dev
# Runs on http://localhost:3000
```

**Initialize System:**
```bash
python main.py init
# Creates directories, sets up default keybinds
```

### Frontend Development

**Development Mode:**
```bash
cd frontend-nextjs
npm run dev
```

**Production Build:**
```bash
cd frontend-nextjs
npm run build
npm start
```

**Linting:**
```bash
cd frontend-nextjs
npm run lint
```

### Testing

```bash
# Backend tests
pip install pytest pytest-asyncio
pytest

# Frontend tests (to be implemented)
cd frontend-nextjs
npm test
```

## Privacy & Security

- **Local-Only**: All data stored locally in SQLite database on your device
- **No Cloud**: No data transmitted to external services (unless using OpenAI)
- **User Control**: Full control over what's captured, stored, and deleted
- **Opt-In Capture**: Capture service only activates on explicit keybind press
- **Open Source**: Full transparency - inspect and modify the code

## Troubleshooting

### Ollama Connection Error

**Issue**: Cannot connect to Ollama service

**Solution**:
1. Ensure Ollama is running:
   ```bash
   ollama serve
   ```

2. Verify models are pulled:
   ```bash
   ollama pull nomic-embed-text
   ollama pull llama3.1:8b
   ```

3. Check Ollama is accessible:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Frontend Cannot Connect to Backend

**Issue**: Frontend shows connection errors

**Solution**:
1. Verify backend is running on port 8000
2. Check backend logs for errors
3. Ensure CORS is configured (already set in `backend/api.py`)
4. Verify `.env` has correct `BACKEND_PORT=8000`

### Tesseract Not Found

**Issue**: Screenshot OCR fails

**Solution**:
- **Windows**: 
  1. Install from https://github.com/UB-Mannheim/tesseract/wiki
  2. Add installation directory to system PATH
  3. Restart terminal
- **Mac**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`
- Verify: `tesseract --version`

### Port Already in Use

**Issue**: Port 8000 or 3000 already occupied

**Solution**:
- **Backend**: Change `BACKEND_PORT` in `.env`
- **Frontend**: Change port in `frontend-nextjs/package.json`:
  ```json
  "dev": "next dev -p 3001"
  ```

### Node Modules Issues

**Issue**: Frontend build errors

**Solution**:
```bash
cd frontend-nextjs
rm -rf node_modules package-lock.json
npm install
```

### Python Dependencies Issues

**Issue**: Import errors or missing packages

**Solution**:
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Features Implemented

- ✅ Background text capture via global keybinds
- ✅ OCR screenshot capture with Tesseract
- ✅ Document upload (TXT, PDF, DOCX)
- ✅ SQLite database with SQLAlchemy ORM
- ✅ FAISS vector store for semantic search
- ✅ Ollama integration for local LLMs
- ✅ OpenAI integration (optional)
- ✅ FastAPI backend with async support
- ✅ Next.js 14 frontend with TypeScript
- ✅ Real-time streaming responses
- ✅ Dark mode with system preference detection
- ✅ Responsive design for all screen sizes
- ✅ RESTful API with OpenAPI documentation

## Future Enhancements

- [ ] Browser extension for web page capture
- [ ] Advanced filtering and tagging system
- [ ] Export capabilities (JSON, CSV, Markdown)
- [ ] Multi-modal support (images, audio transcription)
- [ ] Cloud sync option (optional, encrypted)
- [ ] Mobile companion app
- [ ] Custom keybind configuration UI
- [ ] Automated testing suite

## Contributing

This project was developed as part of CS146S at Stanford University. Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Authors

**Advit Deepak** & **Sriram Varun Vobilisetty**  
CS146S: Principles of Computer System Design  
Stanford University - Autumn 2024

## Acknowledgments

- Built with [Ollama](https://ollama.ai) for local LLM inference
- UI components from [shadcn/ui](https://ui.shadcn.com)
- Vector search powered by [FAISS](https://github.com/facebookresearch/faiss)
- OCR by [Tesseract](https://github.com/tesseract-ocr/tesseract)

---

**Note**: This is a privacy-first tool designed for personal knowledge management. All data stays on your device unless you explicitly configure cloud services.
