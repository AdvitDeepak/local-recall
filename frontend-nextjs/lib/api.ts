import type {
  Stats,
  SystemStatus,
  DataEntry,
  SearchResult,
  RAGResponse,
  Keybind,
  Notification,
  QueryRequest,
  UploadRequest,
} from "./types"
import { mockApi } from "./mock-api"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"
const USE_MOCK_API = process.env.NEXT_PUBLIC_USE_MOCK_API === "true"

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
  getStats: (): Promise<Stats> =>
    USE_MOCK_API ? mockApi.getStats() : fetchAPI("/stats"),

  getStatus: (): Promise<SystemStatus> =>
    fetchAPI("/status"),

  getData: (params?: {
    source?: string
    tag?: string
    limit?: number
  }): Promise<DataEntry[]> => {
    if (USE_MOCK_API) return mockApi.getData(params)

    const searchParams = new URLSearchParams()
    if (params?.source) searchParams.append("source", params.source)
    if (params?.tag) searchParams.append("tag", params.tag)
    if (params?.limit) searchParams.append("limit", params.limit.toString())

    return fetchAPI(`/data?${searchParams.toString()}`)
  },

  deleteEntry: (id: number): Promise<{ message: string }> =>
    USE_MOCK_API
      ? mockApi.deleteEntry(id)
      : fetchAPI(`/data/${id}`, { method: "DELETE" }),

  createEntry: (data: UploadRequest): Promise<DataEntry> =>
    USE_MOCK_API
      ? mockApi.createEntry(data)
      : fetchAPI("/data", {
          method: "POST",
          body: JSON.stringify(data),
        }),

  query: (request: QueryRequest): Promise<RAGResponse> =>
    USE_MOCK_API
      ? mockApi.query(request)
      : fetchAPI("/query", {
          method: "POST",
          body: JSON.stringify(request),
        }),

  queryStream: (request: QueryRequest): EventSource => {
    if (USE_MOCK_API) return mockApi.queryStream(request)

    const searchParams = new URLSearchParams()
    searchParams.append("query", request.query)
    searchParams.append("model", request.model)
    searchParams.append("k", request.k.toString())

    return new EventSource(
      `${API_BASE_URL}/query/stream?${searchParams.toString()}`
    )
  },

  search: (query: string, k: number = 5): Promise<SearchResult[]> => {
    if (USE_MOCK_API) return mockApi.search(query, k)

    const searchParams = new URLSearchParams()
    searchParams.append("query", query)
    searchParams.append("k", k.toString())

    return fetchAPI(`/search?${searchParams.toString()}`)
  },

  getKeybinds: (): Promise<Keybind[]> =>
    USE_MOCK_API ? mockApi.getKeybinds() : fetchAPI("/keybinds"),

  addSelectedTextKeybind: (keySequence: string): Promise<Keybind> =>
    USE_MOCK_API
      ? mockApi.addSelectedTextKeybind(keySequence)
      : fetchAPI("/keybind/selected", {
          method: "POST",
          body: JSON.stringify({ key_sequence: keySequence }),
        }),

  addScreenshotKeybind: (keySequence: string): Promise<Keybind> =>
    USE_MOCK_API
      ? mockApi.addScreenshotKeybind(keySequence)
      : fetchAPI("/keybind/screenshot", {
          method: "POST",
          body: JSON.stringify({ key_sequence: keySequence }),
        }),

  getNotifications: async (params?: {
    since_id?: number
    unread_only?: boolean
    limit?: number
  }): Promise<{ notifications: Notification[] }> => {
    if (USE_MOCK_API) return { notifications: await mockApi.getNotifications(params) }

    const searchParams = new URLSearchParams()
    if (params?.since_id !== undefined)
      searchParams.append("since_id", params.since_id.toString())
    if (params?.unread_only !== undefined)
      searchParams.append("unread_only", params.unread_only.toString())
    if (params?.limit) searchParams.append("limit", params.limit.toString())

    return fetchAPI(`/notifications?${searchParams.toString()}`)
  },

  markNotificationRead: (id: number): Promise<{ message: string }> =>
    USE_MOCK_API
      ? mockApi.markNotificationRead(id)
      : fetchAPI(`/notifications/${id}/read`, { method: "POST" }),

  markAllNotificationsRead: (): Promise<{ message: string }> =>
    USE_MOCK_API
      ? mockApi.markAllNotificationsRead()
      : fetchAPI("/notifications/read-all", { method: "POST" }),

  startCapture: (): Promise<{ status: string }> =>
    fetchAPI("/control/start", { method: "POST" }),

  stopCapture: (): Promise<{ status: string }> =>
    fetchAPI("/control/stop", { method: "POST" }),
}
