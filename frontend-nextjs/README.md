# Local Recall Frontend

A modern, premium Next.js 14 dashboard for Local Recall - a privacy-first RAG system with local text capture and semantic search.

## Features

- **Search & Query**: AI-powered semantic search with RAG capabilities
  - Support for both Ollama (local) and OpenAI models
  - Streaming responses with typewriter effect
  - Relevance scoring with color-coded results
  - Source attribution

- **Data Browser**: Manage captured entries
  - Filter by source, tags, and limit
  - Expandable text preview
  - Delete with confirmation
  - Relative timestamps

- **Upload**: Document management
  - Drag-and-drop file upload
  - Support for TXT, PDF, DOCX
  - Tag-based organization
  - Progress feedback

- **Settings**: System configuration
  - Platform-specific keybind display (macOS/Windows/Linux)
  - System configuration overview
  - OpenAI integration status

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **Icons**: Lucide React
- **Animations**: Framer Motion
- **State**: Zustand
- **Forms**: react-hook-form + zod
- **Date**: date-fns
- **Markdown**: react-markdown

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running at `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Configure environment (already set):
```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Development

Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

Build for production:
```bash
npm run build
```

Start production server:
```bash
npm start
```

## Project Structure

```
frontend-nextjs/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Main page
│   └── globals.css        # Global styles
├── components/
│   ├── layout/            # Layout components
│   │   ├── sidebar.tsx
│   │   └── header.tsx
│   ├── tabs/              # Tab components
│   │   ├── search-tab.tsx
│   │   ├── data-tab.tsx
│   │   ├── upload-tab.tsx
│   │   └── settings-tab.tsx
│   └── ui/                # shadcn/ui components
├── lib/
│   ├── api.ts             # API client
│   ├── types.ts           # TypeScript types
│   ├── utils.ts           # Utilities
│   └── hooks/             # Custom hooks
│       ├── use-toast.ts
│       └── use-theme.ts
└── ...config files
```

## Features in Detail

### Dark Mode
- Auto-detects system preference
- Persistent across sessions
- Smooth transitions

### Real-time Updates
- System stats refresh every 2 seconds
- Live capture status indicator

### Responsive Design
- Mobile-first approach
- Collapsible sidebar
- Adaptive layouts

### Accessibility
- ARIA labels
- Keyboard navigation
- Focus indicators
- Screen reader friendly

## API Integration

The frontend connects to the backend API at `http://localhost:8000`:

- `GET /stats` - System statistics
- `GET /data` - Get captured entries
- `POST /query` - RAG query
- `POST /query/stream` - Streaming query (SSE)
- `GET /search` - Semantic search
- `POST /data` - Create entry
- `DELETE /data/{id}` - Delete entry
- `GET /keybinds` - Get keybinds
- `GET /notifications` - Get notifications

## Customization

### Colors
Edit `app/globals.css` to customize the color scheme. The default uses purple/blue gradients.

### Components
All UI components are in `components/ui/` and can be customized individually.

### API Base URL
Change `NEXT_PUBLIC_API_BASE_URL` in `.env.local` if your backend runs on a different port.

## Troubleshooting

### Backend Connection Issues
- Ensure the backend is running at `http://localhost:8000`
- Check CORS settings in the backend
- Verify `.env.local` has the correct API URL

### Build Errors
- Run `npm install` to ensure all dependencies are installed
- Clear `.next` folder: `rm -rf .next`
- Check for TypeScript errors: `npm run lint`

## License

MIT
