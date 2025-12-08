# Local Recall - Next.js Frontend Setup

A brand new, modern Next.js 14 frontend has been created for Local Recall!

## Overview

The new frontend is a premium, responsive dashboard with:

### Features
- **Search & Query Tab**: AI-powered semantic search with RAG, streaming responses, and source attribution
- **Data Browser Tab**: Browse, filter, and manage captured entries with expandable previews
- **Upload Tab**: Drag-and-drop file upload for TXT, PDF, and DOCX files with tag support
- **Settings Tab**: View keybinds, system configuration, and OpenAI integration status

### Design Highlights
- Modern glass morphism effects
- Dark mode support with system preference detection
- Smooth animations and transitions
- Responsive mobile-first design
- Collapsible sidebar navigation
- Real-time system statistics
- Toast notifications
- Relevance-scored search results with color coding

## Quick Start

### 1. Start the Backend (if not already running)

```bash
# From project root
python main.py
```

The backend should be running at `http://localhost:8000`

### 2. Start the Frontend

```bash
# Navigate to the frontend directory
cd frontend-nextjs

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Alternative: Use Start Scripts

**On macOS/Linux:**
```bash
cd frontend-nextjs
./start-frontend.sh
```

**On Windows:**
```bash
cd frontend-nextjs
start-frontend.bat
```

## Project Structure

```
frontend-nextjs/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout with Inter font
│   ├── page.tsx           # Main page with tab switching
│   └── globals.css        # Global styles and theme
├── components/
│   ├── layout/            # Layout components
│   │   ├── sidebar.tsx    # Collapsible sidebar navigation
│   │   └── header.tsx     # Header with stats and dark mode toggle
│   ├── tabs/              # Main feature tabs
│   │   ├── search-tab.tsx # Search & Query with RAG
│   │   ├── data-tab.tsx   # Data Browser
│   │   ├── upload-tab.tsx # File Upload
│   │   └── settings-tab.tsx # Settings
│   └── ui/                # shadcn/ui components
├── lib/
│   ├── api.ts             # API client for backend
│   ├── types.ts           # TypeScript type definitions
│   ├── utils.ts           # Utility functions
│   └── hooks/             # Custom React hooks
│       ├── use-toast.ts   # Toast notifications
│       └── use-theme.ts   # Dark mode support
└── README.md              # Detailed documentation
```

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - High-quality component library
- **Lucide React** - Icon library
- **Framer Motion** - Smooth animations
- **Zustand** - State management
- **react-hook-form + zod** - Form validation
- **date-fns** - Date formatting
- **react-markdown** - Markdown rendering for AI answers

## Key Features Explained

### Search & Query Tab
- Choose between Ollama (local) or OpenAI models
- Toggle RAG mode for AI-powered answers
- Enable streaming for real-time typewriter effect
- Adjust number of results with slider (1-10)
- View relevance scores with color-coded indicators:
  - Green: >80% relevance
  - Yellow: 60-80% relevance
  - Orange: <60% relevance

### Data Browser Tab
- Filter by source (clipboard, screenshot, or all)
- Filter by tags (for uploaded documents)
- Set result limit (10-500 entries)
- Expandable text previews
- Delete entries with confirmation dialog
- Relative timestamps ("2 hours ago")

### Upload Tab
- Drag-and-drop interface
- Support for TXT, PDF, DOCX files
- Add multiple tags per upload
- Visual file list with size display
- Batch upload with progress feedback

### Settings Tab
- Platform-specific keybind display (auto-detects macOS/Windows)
- System configuration overview
- OpenAI API status
- About section with feature list

## Configuration

The frontend is already configured to connect to the backend at `http://localhost:8000`.

If you need to change this:

1. Edit `frontend-nextjs/.env.local`:
```bash
NEXT_PUBLIC_API_BASE_URL=http://your-backend-url:port
```

2. Restart the development server

## Dark Mode

Dark mode is automatically detected from your system preferences and persisted across sessions. Toggle manually using the moon/sun icon in the header.

## Development

### Install Dependencies
```bash
npm install
```

### Run Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

### Start Production Server
```bash
npm start
```

### Lint Code
```bash
npm run lint
```

## Troubleshooting

### Backend Connection Errors
- Ensure the Python backend is running at `http://localhost:8000`
- Check that CORS is properly configured in the backend
- Verify the API URL in `.env.local`

### Module Not Found Errors
```bash
rm -rf node_modules package-lock.json
npm install
```

### Build Errors
```bash
rm -rf .next
npm run build
```

### Port Already in Use
If port 3000 is already in use, you can start on a different port:
```bash
npm run dev -- -p 3001
```

## API Endpoints Used

The frontend communicates with these backend endpoints:

- `GET /stats` - System statistics (auto-refreshes every 2 seconds)
- `GET /data` - Get captured entries with filters
- `DELETE /data/{id}` - Delete entry
- `POST /data` - Create entry (for uploads)
- `POST /query` - RAG query (non-streaming)
- `POST /query/stream` - RAG query (streaming with SSE)
- `GET /search` - Semantic search only
- `GET /keybinds` - Get configured keybinds
- `GET /notifications` - Get system notifications

## Comparison: Old vs New Frontend

### Old Frontend (Gradio)
- Simple, functional interface
- Limited styling options
- Desktop-focused
- Basic file uploads
- No dark mode
- No animations

### New Frontend (Next.js)
- Modern, premium design
- Fully customizable
- Responsive (mobile, tablet, desktop)
- Advanced file upload with drag-and-drop
- Dark mode support
- Smooth animations and transitions
- Better error handling
- Toast notifications
- Collapsible sidebar
- Real-time stats
- Streaming responses with typewriter effect

## Next Steps

1. Start the backend: `python main.py`
2. Start the frontend: `cd frontend-nextjs && npm run dev`
3. Open http://localhost:3000
4. Try searching your captured data
5. Upload some documents
6. Explore the settings

## Need Help?

- Frontend documentation: `frontend-nextjs/README.md`
- Backend documentation: `README.md` (in project root)
- Issues with the UI: Check browser console for errors
- Issues with API: Check backend logs

Enjoy your new premium Local Recall frontend!
