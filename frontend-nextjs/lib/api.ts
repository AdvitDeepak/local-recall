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

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = "APIError"
  }
}

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new APIError(response.status, `API Error: ${response.statusText}`)
  }

  return response.json()
}

export const api = {
  getStats: (): Promise<Stats> => fetchAPI("/stats"),

  getData: (params?: {
    source?: string
    tag?: string
    limit?: number
  }): Promise<DataEntry[]> => {
    const searchParams = new URLSearchParams()
    if (params?.source) searchParams.append("source", params.source)
    if (params?.tag) searchParams.append("tag", params.tag)
    if (params?.limit) searchParams.append("limit", params.limit.toString())

    return fetchAPI(`/data?${searchParams.toString()}`)
  },

  deleteEntry: (id: number): Promise<{ message: string }> =>
    fetchAPI(`/data/${id}`, { method: "DELETE" }),

  createEntry: (data: UploadRequest): Promise<DataEntry> =>
    fetchAPI("/data", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  query: (request: QueryRequest): Promise<RAGResponse> =>
    fetchAPI("/query", {
      method: "POST",
      body: JSON.stringify(request),
    }),

  queryStream: (request: QueryRequest): EventSource => {
    const searchParams = new URLSearchParams()
    searchParams.append("query", request.query)
    searchParams.append("model", request.model)
    searchParams.append("k", request.k.toString())

    return new EventSource(
      `${API_BASE_URL}/query/stream?${searchParams.toString()}`
    )
  },

  search: (query: string, k: number = 5): Promise<SearchResult[]> => {
    const searchParams = new URLSearchParams()
    searchParams.append("query", query)
    searchParams.append("k", k.toString())

    return fetchAPI(`/search?${searchParams.toString()}`)
  },

  getKeybinds: (): Promise<Keybind[]> => fetchAPI("/keybinds"),

  addSelectedTextKeybind: (keySequence: string): Promise<Keybind> =>
    fetchAPI("/keybind/selected", {
      method: "POST",
      body: JSON.stringify({ key_sequence: keySequence }),
    }),

  addScreenshotKeybind: (keySequence: string): Promise<Keybind> =>
    fetchAPI("/keybind/screenshot", {
      method: "POST",
      body: JSON.stringify({ key_sequence: keySequence }),
    }),

  getNotifications: (params?: {
    since_id?: number
    unread_only?: boolean
    limit?: number
  }): Promise<Notification[]> => {
    const searchParams = new URLSearchParams()
    if (params?.since_id !== undefined)
      searchParams.append("since_id", params.since_id.toString())
    if (params?.unread_only !== undefined)
      searchParams.append("unread_only", params.unread_only.toString())
    if (params?.limit) searchParams.append("limit", params.limit.toString())

    return fetchAPI(`/notifications?${searchParams.toString()}`)
  },

  markNotificationRead: (id: number): Promise<{ message: string }> =>
    fetchAPI(`/notifications/${id}/read`, { method: "POST" }),

  markAllNotificationsRead: (): Promise<{ message: string }> =>
    fetchAPI("/notifications/read-all", { method: "POST" }),
}
