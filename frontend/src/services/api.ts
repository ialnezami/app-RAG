import axios, { AxiosInstance, AxiosResponse } from 'axios'
import toast from 'react-hot-toast'
import {
  Profile,
  CreateProfileRequest,
  UpdateProfileRequest,
  Document,
  SearchRequest,
  SearchResponse,
  ChatSession,
  CreateSessionRequest,
  SendMessageRequest,
  SendMessageResponse,
  ChatQueryRequest,
  ChatQueryResponse,
  ProvidersResponse,
  HealthStatus,
  DetailedStatus,
  DocumentChunk,
  ApiError
} from './types'

class ApiService {
  private api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response
      },
      (error) => {
        const apiError: ApiError = error.response?.data || {
          error: 'Network error',
          code: 'NETWORK_ERROR',
          details: 'Unable to connect to the server'
        }
        
        // Show error toast
        toast.error(apiError.error || 'An error occurred')
        
        return Promise.reject(apiError)
      }
    )
  }

  // Health endpoints
  async getHealth(): Promise<HealthStatus> {
    const response = await this.api.get('/health')
    return response.data
  }

  async getStatus(): Promise<DetailedStatus> {
    const response = await this.api.get('/status')
    return response.data
  }

  // Profile endpoints
  async getProfiles(page = 1, limit = 50): Promise<{ profiles: Profile[], total: number, page: number, limit: number }> {
    const response = await this.api.get('/api/v1/profiles', {
      params: { page, limit }
    })
    return response.data
  }

  async getProfile(id: number): Promise<Profile> {
    const response = await this.api.get(`/api/v1/profiles/${id}`)
    return response.data
  }

  async createProfile(data: CreateProfileRequest): Promise<Profile> {
    const response = await this.api.post('/api/v1/profiles', data)
    toast.success('Profile created successfully')
    return response.data
  }

  async updateProfile(id: number, data: UpdateProfileRequest): Promise<Profile> {
    const response = await this.api.put(`/api/v1/profiles/${id}`, data)
    toast.success('Profile updated successfully')
    return response.data
  }

  async deleteProfile(id: number): Promise<void> {
    await this.api.delete(`/api/v1/profiles/${id}`)
    toast.success('Profile deleted successfully')
  }

  async getProfileStats(id: number): Promise<any> {
    const response = await this.api.get(`/api/v1/profiles/${id}/stats`)
    return response.data
  }

  async getAvailableProviders(): Promise<ProvidersResponse> {
    const response = await this.api.get('/api/v1/config/providers')
    return response.data
  }

  async getAvailableModels(provider?: string): Promise<any> {
    const params = provider ? { provider } : {}
    const response = await this.api.get('/api/v1/config/models', { params })
    return response.data
  }

  // Document endpoints
  async getDocuments(profileId?: number, page = 1, limit = 50): Promise<{ documents: Document[], total: number, page: number, limit: number }> {
    const params: any = { page, limit }
    if (profileId) params.profile_id = profileId
    
    const response = await this.api.get('/api/v1/documents', { params })
    return response.data
  }

  async getDocument(id: string): Promise<Document> {
    const response = await this.api.get(`/api/v1/documents/${id}`)
    return response.data
  }

  async uploadDocument(file: File, profileId: number, onProgress?: (progress: number) => void): Promise<Document> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('profile_id', profileId.toString())

    const response = await this.api.post('/api/v1/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
    
    toast.success('Document uploaded successfully')
    return response.data
  }

  async processDocument(documentId: string, profileId: number): Promise<any> {
    const response = await this.api.post('/api/v1/documents/process', {
      document_id: documentId,
      profile_id: profileId
    })
    toast.success('Document processing started')
    return response.data
  }

  async deleteDocument(id: string): Promise<void> {
    await this.api.delete(`/api/v1/documents/${id}`)
    toast.success('Document deleted successfully')
  }

  async searchDocuments(request: SearchRequest): Promise<SearchResponse> {
    const response = await this.api.post('/api/v1/search', request)
    return response.data
  }

  async searchSimilarChunks(request: SearchRequest): Promise<SearchResponse> {
    const response = await this.api.post('/api/v1/search/similar', request)
    return response.data
  }

  async getDocumentChunks(documentId: string): Promise<{ document_id: string, chunks: DocumentChunk[], total_chunks: number }> {
    const response = await this.api.get(`/api/v1/documents/${documentId}/chunks`)
    return response.data
  }

  // Chat endpoints
  async getChatSessions(profileId?: number, page = 1, limit = 50): Promise<{ sessions: ChatSession[], total: number, page: number, limit: number }> {
    const params: any = { page, limit }
    if (profileId) params.profile_id = profileId
    
    const response = await this.api.get('/api/v1/chat/sessions', { params })
    return response.data
  }

  async getChatSession(id: string): Promise<ChatSession> {
    const response = await this.api.get(`/api/v1/chat/sessions/${id}`)
    return response.data
  }

  async createChatSession(data: CreateSessionRequest): Promise<ChatSession> {
    const response = await this.api.post('/api/v1/chat/sessions', data)
    toast.success('Chat session created')
    return response.data
  }

  async sendMessage(data: SendMessageRequest): Promise<SendMessageResponse> {
    const response = await this.api.post('/api/v1/chat/query', data)
    return response.data
  }

  async queryDirect(data: ChatQueryRequest): Promise<ChatQueryResponse> {
    const response = await this.api.post('/api/v1/chat/query-direct', data)
    return response.data
  }

  async deleteChatSession(id: string): Promise<void> {
    await this.api.delete(`/api/v1/chat/sessions/${id}`)
    toast.success('Chat session deleted')
  }

  async getSessionMessages(sessionId: string, limit = 100, offset = 0): Promise<any> {
    const response = await this.api.get(`/api/v1/chat/sessions/${sessionId}/messages`, {
      params: { limit, offset }
    })
    return response.data
  }

  // Utility methods
  async testConnection(): Promise<boolean> {
    try {
      await this.getHealth()
      return true
    } catch {
      return false
    }
  }

  setBaseURL(url: string): void {
    this.api.defaults.baseURL = url
  }

  getBaseURL(): string {
    return this.api.defaults.baseURL || ''
  }
}

// Export singleton instance
export const apiService = new ApiService()
export default apiService
