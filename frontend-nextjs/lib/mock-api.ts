import type {
  Stats,
  DataEntry,
  SearchResult,
  RAGResponse,
  Keybind,
  Notification,
  QueryRequest,
  UploadRequest,
} from "./types"

const mockEntries: DataEntry[] = [
  {
    id: 1,
    text: "React is a JavaScript library for building user interfaces. It lets you create reusable components and manage state efficiently.",
    source: "clipboard",
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    tags: [],
    char_count: 134,
  },
  {
    id: 2,
    text: "Next.js is a React framework that enables server-side rendering and static site generation. It provides features like file-based routing, API routes, and automatic code splitting.",
    source: "clipboard",
    timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    tags: ["documentation"],
    char_count: 189,
  },
  {
    id: 3,
    text: "TypeScript adds static typing to JavaScript, helping catch errors early in development and improving code maintainability.",
    source: "screenshot",
    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    tags: [],
    char_count: 131,
  },
  {
    id: 4,
    text: "Tailwind CSS is a utility-first CSS framework that provides low-level utility classes for building custom designs without writing CSS.",
    source: "clipboard",
    timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ["css", "documentation"],
    char_count: 138,
  },
  {
    id: 5,
    text: "Local Recall is a privacy-first RAG system that captures text locally and provides semantic search capabilities.",
    source: "upload",
    timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    tags: ["project"],
    char_count: 118,
  },
]

const mockKeybinds: Keybind[] = [
  {
    id: 1,
    key_sequence: "Cmd+Ctrl+R",
    action: "capture_selected",
    platform: "macos",
  },
  {
    id: 2,
    key_sequence: "Cmd+Ctrl+T",
    action: "capture_screenshot",
    platform: "macos",
  },
  {
    id: 3,
    key_sequence: "Ctrl+Alt+R",
    action: "capture_selected",
    platform: "windows",
  },
  {
    id: 4,
    key_sequence: "Ctrl+Alt+T",
    action: "capture_screenshot",
    platform: "windows",
  },
]

let mockStats: Stats = {
  total_entries: 5,
  embedded_entries: 5,
  is_capturing: true,
}

function delay(ms: number = 500): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export const mockApi = {
  getStats: async (): Promise<Stats> => {
    await delay(300)
    mockStats.is_capturing = Math.random() > 0.3
    return mockStats
  },

  getData: async (params?: {
    source?: string
    tag?: string
    limit?: number
  }): Promise<DataEntry[]> => {
    await delay(500)
    let filtered = [...mockEntries]

    if (params?.source) {
      filtered = filtered.filter((e) => e.source === params.source)
    }

    if (params?.tag) {
      filtered = filtered.filter(
        (e) => e.tags && e.tags.some((t) => t.includes(params.tag!))
      )
    }

    const limit = params?.limit || 50
    return filtered.slice(0, limit)
  },

  deleteEntry: async (id: number): Promise<{ message: string }> => {
    await delay(300)
    const index = mockEntries.findIndex((e) => e.id === id)
    if (index > -1) {
      mockEntries.splice(index, 1)
      mockStats.total_entries--
      mockStats.embedded_entries--
    }
    return { message: "Entry deleted successfully" }
  },

  createEntry: async (data: UploadRequest): Promise<DataEntry> => {
    await delay(800)
    const newEntry: DataEntry = {
      id: Math.max(...mockEntries.map((e) => e.id)) + 1,
      text: data.text,
      source: data.source,
      timestamp: new Date().toISOString(),
      tags: data.tags || [],
      char_count: data.text.length,
    }
    mockEntries.unshift(newEntry)
    mockStats.total_entries++
    mockStats.embedded_entries++
    return newEntry
  },

  query: async (request: QueryRequest): Promise<RAGResponse> => {
    await delay(1500)
    const searchResults = await mockApi.search(request.query, request.k)

    return {
      answer: `Based on your query "${request.query}", I found relevant information in your captured data. ${searchResults[0]?.entry.text.substring(0, 100)}... This information relates to ${request.query} and provides context about the topic you're asking about.`,
      sources: searchResults,
      model: request.model,
      query: request.query,
    }
  },

  queryStream: (request: QueryRequest): EventSource => {
    const mockEventSource = new EventTarget() as any
    mockEventSource.close = () => {}

    setTimeout(async () => {
      const answer = `Based on your query "${request.query}", here's what I found in your knowledge base. `
      const words = answer.split(" ")

      for (let i = 0; i < words.length; i++) {
        await delay(50)
        const event = new MessageEvent("message", {
          data: JSON.stringify({
            type: "token",
            content: words[i] + " ",
          }),
        })
        mockEventSource.dispatchEvent(event)
      }

      await delay(200)
      const searchResults = await mockApi.search(request.query, request.k)
      const sourcesEvent = new MessageEvent("message", {
        data: JSON.stringify({
          type: "sources",
          content: searchResults,
        }),
      })
      mockEventSource.dispatchEvent(sourcesEvent)

      await delay(100)
      const doneEvent = new MessageEvent("message", {
        data: JSON.stringify({ type: "done" }),
      })
      mockEventSource.dispatchEvent(doneEvent)
    }, 100)

    return mockEventSource as EventSource
  },

  search: async (query: string, k: number = 5): Promise<SearchResult[]> => {
    await delay(700)
    const queryLower = query.toLowerCase()

    return mockEntries
      .map((entry) => {
        const textLower = entry.text.toLowerCase()
        const hasMatch = textLower.includes(queryLower)
        const relevance = hasMatch
          ? 0.7 + Math.random() * 0.25
          : 0.3 + Math.random() * 0.4

        return {
          entry,
          relevance_score: relevance,
        }
      })
      .sort((a, b) => b.relevance_score - a.relevance_score)
      .slice(0, k)
  },

  getKeybinds: async (): Promise<Keybind[]> => {
    await delay(400)
    return mockKeybinds
  },

  addSelectedTextKeybind: async (keySequence: string): Promise<Keybind> => {
    await delay(300)
    const newKeybind: Keybind = {
      id: mockKeybinds.length + 1,
      key_sequence: keySequence,
      action: "capture_selected",
      platform: "all",
    }
    mockKeybinds.push(newKeybind)
    return newKeybind
  },

  addScreenshotKeybind: async (keySequence: string): Promise<Keybind> => {
    await delay(300)
    const newKeybind: Keybind = {
      id: mockKeybinds.length + 1,
      key_sequence: keySequence,
      action: "capture_screenshot",
      platform: "all",
    }
    mockKeybinds.push(newKeybind)
    return newKeybind
  },

  getNotifications: async (params?: {
    since_id?: number
    unread_only?: boolean
    limit?: number
  }): Promise<Notification[]> => {
    await delay(300)
    return [
      {
        id: 1,
        message: "5 new entries captured",
        type: "info",
        timestamp: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
        read: false,
      },
    ]
  },

  markNotificationRead: async (id: number): Promise<{ message: string }> => {
    await delay(200)
    return { message: "Notification marked as read" }
  },

  markAllNotificationsRead: async (): Promise<{ message: string }> => {
    await delay(200)
    return { message: "All notifications marked as read" }
  },
}
