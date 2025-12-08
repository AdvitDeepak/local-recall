export interface Stats {
  total_entries: number
  embedded_entries: number
  is_capturing: boolean
}

export interface DataEntry {
  id: number
  text: string
  source: string
  timestamp: string
  tags?: string[]
  char_count: number
}

export interface SearchResult {
  entry: DataEntry
  relevance_score: number
}

export interface RAGResponse {
  answer: string
  sources: SearchResult[]
  model: string
  query: string
}

export interface Keybind {
  id: number
  key_sequence: string
  action: string
  platform: string
}

export interface Notification {
  id: number
  message: string
  type: string
  timestamp: string
  read: boolean
}

export interface QueryRequest {
  query: string
  model: string
  k: number
}

export interface UploadRequest {
  text: string
  source: string
  tags?: string[]
}
