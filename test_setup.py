"""Test script to verify Local Recall installation."""
import sys
from pathlib import Path


def test_python_version():
    """Test Python version."""
    print("Testing Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[FAIL] Python {version.major}.{version.minor}.{version.micro} - Need Python 3.9+")
        return False


def test_imports():
    """Test required package imports."""
    print("\nTesting package imports...")
    packages = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'streamlit': 'Streamlit',
        'sqlalchemy': 'SQLAlchemy',
        'pydantic': 'Pydantic',
        'numpy': 'NumPy',
        'faiss': 'FAISS',
        'ollama': 'Ollama',
        'pynput': 'Pynput',
        'pyperclip': 'Pyperclip',
        'mss': 'MSS',
        'pytesseract': 'Pytesseract',
        'PIL': 'Pillow',
        'fitz': 'PyMuPDF',
        'docx': 'python-docx',
    }

    success = True
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"[OK] {name}")
        except ImportError:
            print(f"[FAIL] {name} - NOT FOUND")
            success = False

    return success


def test_ollama():
    """Test Ollama connection."""
    print("\nTesting Ollama connection...")
    try:
        import ollama
        models = ollama.list()
        print("[OK] Ollama is running")

        # Check for required models
        if isinstance(models, dict) and 'models' in models:
            model_list = models.get('models', [])
            if model_list:
                model_names = [m.get('name', m.get('model', '')) for m in model_list]
            else:
                model_names = []
        else:
            model_names = []

        if any('nomic-embed-text' in name for name in model_names):
            print("[OK] nomic-embed-text model found")
        else:
            print("[WARN] nomic-embed-text model not found - run: ollama pull nomic-embed-text")

        if any('llama3.1' in name for name in model_names):
            print("[OK] llama3.1 model found")
        else:
            print("[WARN] llama3.1 model not found - run: ollama pull llama3.1:8b")

        return True
    except Exception as e:
        print(f"[FAIL] Ollama error: {e}")
        print("  Make sure Ollama is running: ollama serve")
        return False


def test_tesseract():
    """Test Tesseract installation."""
    print("\nTesting Tesseract OCR...")
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"[OK] Tesseract {version}")
        return True
    except Exception as e:
        print(f"[FAIL] Tesseract error: {e}")
        print("  Install Tesseract and add to PATH")
        return False


def test_file_structure():
    """Test project file structure."""
    print("\nTesting project structure...")
    required_files = [
        'config.py',
        'main.py',
        'requirements.txt',
        '.env.example',
        'backend/api.py',
        'frontend/app.py',
        'database/models.py',
        'database/db.py',
        'vector_store/faiss_store.py',
        'embeddings/ollama_embeddings.py',
        'embeddings/pipeline.py',
        'rag/query_engine.py',
        'capture/capture_service.py',
        'utils/document_parser.py',
    ]

    success = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] {file_path} - MISSING")
            success = False

    return success


def test_env_file():
    """Test .env file."""
    print("\nTesting configuration...")
    if Path('.env').exists():
        print("[OK] .env file exists")
        return True
    else:
        print("[WARN] .env file not found")
        print("  Run: cp .env.example .env")
        if Path('.env.example').exists():
            print("  .env.example is available")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Local Recall Setup Test")
    print("=" * 50)

    results = []

    results.append(("Python Version", test_python_version()))
    results.append(("Package Imports", test_imports()))
    results.append(("Ollama", test_ollama()))
    results.append(("Tesseract OCR", test_tesseract()))
    results.append(("File Structure", test_file_structure()))
    results.append(("Configuration", test_env_file()))

    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        symbol = "[OK]" if passed else "[FAIL]"
        print(f"{symbol} {test_name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 50)

    if all_passed:
        print("\n*** All tests passed! You're ready to use Local Recall. ***")
        print("\nNext steps:")
        print("1. Run: python main.py init")
        print("2. Run: python main.py all")
        print("3. Open dashboard: http://localhost:8501")
    else:
        print("\n*** Some tests failed. Please fix the issues above. ***")
        print("\nRefer to SETUP.md for detailed instructions.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
