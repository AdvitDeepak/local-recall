# Local Recall Setup Guide

## Step-by-Step Installation

### 1. Install Prerequisites

#### Ollama (Required)
Download and install from https://ollama.ai

After installation, pull the required models:
```bash
ollama pull nomic-embed-text
ollama pull llama3.1:8b
```

Verify Ollama is running:
```bash
ollama list
```

#### Tesseract OCR (Required for screenshot capture)

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location (C:\Program Files\Tesseract-OCR)
3. Add to PATH: `C:\Program Files\Tesseract-OCR`
4. Verify: `tesseract --version`

**Mac:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

### 2. Set Up Local Recall

#### Option A: Quick Start (Recommended)

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create `.env` configuration
- Start all components

#### Option B: Manual Setup

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create configuration:**
   ```bash
   cp .env.example .env
   ```

5. **Initialize system:**
   ```bash
   python main.py init
   ```

6. **Start components:**

   Run all at once:
   ```bash
   python main.py all
   ```

   Or run separately in different terminals:
   ```bash
   # Terminal 1: Backend
   python main.py backend

   # Terminal 2: Frontend
   python main.py frontend

   # Terminal 3: Capture service
   python main.py capture
   ```

### 3. Verify Installation

Once running, you should see:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Dashboard: http://localhost:8501

Test the system:
1. Open the dashboard at http://localhost:8501
2. Check that all statistics show "0" (empty database)
3. Try uploading a text file
4. Try searching for content

### 4. Using the System

#### Capture Text

**Default Keybinds:**
- `Ctrl+Alt+R`: Capture selected text
  1. Select any text
  2. Copy it (Ctrl+C)
  3. Press Ctrl+Alt+R to save to database

- `Ctrl+Alt+T`: Capture screenshot text (OCR)
  1. Press Ctrl+Alt+T
  2. System captures screen and extracts text

#### Upload Documents

1. Go to dashboard "Upload" tab
2. Choose TXT, PDF, or DOCX file
3. Add optional tags
4. Click "Upload & Process"

#### Search & Query

1. Go to "Search & Query" tab
2. Enter your question
3. Choose "Use RAG" for LLM-powered answers
4. Click "Search"

### 5. Common Issues

#### "Ollama connection error"
**Solution:** Start Ollama service
```bash
ollama serve
```

#### "Tesseract not found"
**Solution:** Ensure Tesseract is installed and in PATH
```bash
tesseract --version  # Should show version
```

#### "Port already in use"
**Solution:** Change ports in `.env`:
```env
BACKEND_PORT=8001
FRONTEND_PORT=8502
```

#### "Import errors"
**Solution:** Ensure virtual environment is activated
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### 6. Configuration Options

Edit `.env` file to customize:

```env
# Database location
DATABASE_PATH=./data/local_recall.db

# Vector index location
FAISS_INDEX_PATH=./data/faiss_index

# Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
LLM_MODEL=llama3.1:8b

# Server ports
BACKEND_PORT=8000
FRONTEND_PORT=8501

# Logging
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
```

### 7. Development Workflow

**Starting development:**
```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run backend with auto-reload
uvicorn backend.api:app --reload --port 8000

# In another terminal, run frontend
streamlit run frontend/app.py

# In another terminal, run capture service
python main.py capture
```

**Viewing logs:**
```bash
# Backend logs show in terminal
# Or set LOG_LEVEL=DEBUG in .env for more details
```

**Accessing API:**
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### 8. Testing the RAG System

1. **Add some test data:**
   - Create a file `test.txt` with some content
   - Upload it via dashboard

2. **Wait for embedding:**
   - Check dashboard stats
   - "Embedded Entries" should increase

3. **Try semantic search:**
   - Enter a query related to your content
   - Should return relevant results

4. **Try RAG query:**
   - Enable "Use RAG"
   - Ask a question
   - Should get an LLM-generated answer with sources

### 9. Next Steps

- Add more documents to build your knowledge base
- Customize keybinds in Settings
- Try different Ollama models
- Explore API endpoints for integration

### 10. Stopping the System

**If running with `start.bat` or `start.sh`:**
```
Press Ctrl+C
```

**If running components separately:**
- Stop each terminal with Ctrl+C

**To completely clean up:**
```bash
# Deactivate virtual environment
deactivate
```

## Support

For issues or questions, refer to:
- Main README.md
- API documentation at http://localhost:8000/docs
- Project proposal in CLAUDE.md
