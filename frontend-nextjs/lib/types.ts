export interface Stats {
  total_entries: number
  embedded_entries: number
  is_embedded: boolean
}

export interface SystemStatus {
  capturing: boolean
  database: {
    total_entries: number
    embedded_entries: number
    pending_embeddings: number
  }
  vector_store: {
    total_vectors: number
    dimension: number
  }
  backend_version: string
}

export interface DataEntry {
  id: number
  content: string
  source: string
  capture_method: string
  timestamp: string
  tags: string[]
  is_embedded: boolean
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
  is_active: boolean
  created_at: string
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
