// API Response Types
export interface ApiResponse<T> {
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
}

// Profile Types
export interface Profile {
  id: number
  name: string
  description?: string
  prompt: string
  provider: string
  model: string
  settings: Record<string, any>
  created_at: string
  updated_at: string
}

export interface CreateProfileRequest {
  name: string
  description?: string
  prompt: string
  provider: string
  model: string
  settings: Record<string, any>
}

export interface UpdateProfileRequest {
  name?: string
  description?: string
  prompt?: string
  provider?: string
  model?: string
  settings?: Record<string, any>
}

// Document Types
export interface Document {
  id: string
  filename: string
  original_filename: string
  file_size?: number
  mime_type?: string
  upload_date: string
  processed: boolean
  profile_id: number
  metadata: Record<string, any>
}

export interface DocumentChunk {
  id: string
  chunk_index: number
  content: string
  has_embedding: boolean
  metadata: Record<string, any>
  created_at: string
}

export interface SearchResult {
  id: string
  content: string
  similarity: number
  document_filename: string
  document_id: string
  chunk_index: number
  metadata: Record<string, any>
}

export interface SearchRequest {
  query: string
  profile_id: number
  limit?: number
  similarity_threshold?: number
}

export interface SearchResponse {
  results: SearchResult[]
  total_results: number
  query: string
  search_time: number
}

// Chat Types
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  context_chunks: ContextChunk[]
  timestamp: string
}

export interface ContextChunk {
  id: string
  content: string
  similarity: number
  document_filename?: string
  document_id?: string
  chunk_index: number
  metadata: Record<string, any>
}

export interface ChatSession {
  id: string
  session_name?: string
  profile_id: number
  messages: ChatMessage[]
  created_at: string
  updated_at: string
}

export interface CreateSessionRequest {
  profile_id: number
  session_name?: string
}

export interface SendMessageRequest {
  session_id: string
  message: string
  profile_id: number
  max_context_chunks?: number
}

export interface SendMessageResponse {
  id: string
  role: string
  content: string
  context_chunks: ContextChunk[]
  timestamp: string
  usage?: Record<string, any>
}

export interface ChatQueryRequest {
  query: string
  profile_id: number
  max_context_chunks?: number
}

export interface ChatQueryResponse {
  response: string
  context_chunks: ContextChunk[]
  usage?: Record<string, any>
  search_time: number
}

// AI Provider Types
export interface AIProvider {
  name: string
  base_url: string
  models: Record<string, AIModel>
}

export interface AIModel {
  name: string
  max_tokens?: number
  temperature?: number
  cost_per_1k_tokens?: number
  dimensions?: number
}

export interface ProvidersResponse {
  providers: Record<string, AIProvider>
  total_providers: number
  total_models: number
}

// Health Types
export interface HealthStatus {
  status: string
  timestamp: string
  service: string
  version: string
}

export interface DetailedStatus {
  status: string
  timestamp: string
  service: string
  version: string
  environment: string
  components: {
    database: {
      status: string
      connection: string
    }
    ai_providers: {
      status: string
      available: string[]
      count: number
    }
    embeddings: {
      status: string
      available_providers: Record<string, string[]>
      total_providers: number
    }
  }
  configuration: {
    debug_mode: boolean
    cors_origins: string[]
    max_file_size: number
    allowed_file_types: string[]
  }
}

// WebSocket Types
export interface WebSocketMessage {
  type: string
  [key: string]: any
}

export interface JoinSessionMessage extends WebSocketMessage {
  type: 'join_session'
  session_id: string
}

export interface SendMessageMessage extends WebSocketMessage {
  type: 'send_message'
  session_id: string
  message: string
  profile_id: number
}

export interface TypingMessage extends WebSocketMessage {
  type: 'typing'
  typing: boolean
}

export interface MessageReceivedMessage extends WebSocketMessage {
  type: 'message_received'
  id: string
  role: string
  content: string
  context_chunks: ContextChunk[]
  timestamp: string
  user_id?: string
}

export interface AIStreamingMessage extends WebSocketMessage {
  type: 'ai_streaming'
  chunk: string
  session_id: string
  timestamp: number
}

export interface AIMessageCompleteMessage extends WebSocketMessage {
  type: 'ai_message_complete'
  id: string
  role: string
  content: string
  context_chunks: ContextChunk[]
  timestamp: string
  session_id: string
}

export interface TypingIndicatorMessage extends WebSocketMessage {
  type: 'typing_indicator'
  user_id: string
  typing: boolean
  session_id: string
  timestamp: number
}

export interface SessionJoinedMessage extends WebSocketMessage {
  type: 'session_joined'
  session_id: string
  session_name?: string
  profile_id: number
  timestamp: number
}

export interface SessionCreatedMessage extends WebSocketMessage {
  type: 'session_created'
  session_id: string
  session_name?: string
  profile_id: number
  timestamp: number
}

export interface ErrorMessage extends WebSocketMessage {
  type: 'error'
  message: string
  timestamp: number
}

// Error Types
export interface ApiError {
  error: string
  code: string
  details?: string
}

// File Upload Types
export interface FileUploadProgress {
  file: File
  progress: number
  status: 'uploading' | 'processing' | 'completed' | 'error'
  error?: string
}

// Store Types
export interface AppState {
  profiles: Profile[]
  documents: Document[]
  chatSessions: ChatSession[]
  currentProfile: Profile | null
  currentSession: ChatSession | null
  isLoading: boolean
  error: string | null
}

export interface ChatState {
  sessions: ChatSession[]
  currentSession: ChatSession | null
  isConnected: boolean
  isTyping: boolean
  typingUsers: Set<string>
}

export interface DocumentState {
  documents: Document[]
  uploadProgress: FileUploadProgress[]
  searchResults: SearchResult[]
  isLoading: boolean
  error: string | null
}

export interface ProfileState {
  profiles: Profile[]
  currentProfile: Profile | null
  availableProviders: ProvidersResponse | null
  isLoading: boolean
  error: string | null
}
