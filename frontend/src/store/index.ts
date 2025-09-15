import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { Profile, Document, ChatSession } from '../services/types'

// App Store
interface AppState {
  // State
  profiles: Profile[]
  documents: Document[]
  chatSessions: ChatSession[]
  currentProfile: Profile | null
  currentSession: ChatSession | null
  isLoading: boolean
  error: string | null
  
  // Actions
  setProfiles: (profiles: Profile[]) => void
  addProfile: (profile: Profile) => void
  updateProfile: (id: number, profile: Profile) => void
  removeProfile: (id: number) => void
  setCurrentProfile: (profile: Profile | null) => void
  
  setDocuments: (documents: Document[]) => void
  addDocument: (document: Document) => void
  updateDocument: (id: string, document: Document) => void
  removeDocument: (id: string) => void
  
  setChatSessions: (sessions: ChatSession[]) => void
  addChatSession: (session: ChatSession) => void
  updateChatSession: (id: string, session: ChatSession) => void
  removeChatSession: (id: string) => void
  setCurrentSession: (session: ChatSession | null) => void
  
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        profiles: [],
        documents: [],
        chatSessions: [],
        currentProfile: null,
        currentSession: null,
        isLoading: false,
        error: null,

        // Profile actions
        setProfiles: (profiles) => set({ profiles }),
        addProfile: (profile) => set((state) => ({ 
          profiles: [...state.profiles, profile] 
        })),
        updateProfile: (id, profile) => set((state) => ({
          profiles: state.profiles.map(p => p.id === id ? profile : p)
        })),
        removeProfile: (id) => set((state) => ({
          profiles: state.profiles.filter(p => p.id !== id),
          currentProfile: state.currentProfile?.id === id ? null : state.currentProfile
        })),
        setCurrentProfile: (profile) => set({ currentProfile: profile }),

        // Document actions
        setDocuments: (documents) => set({ documents }),
        addDocument: (document) => set((state) => ({ 
          documents: [...state.documents, document] 
        })),
        updateDocument: (id, document) => set((state) => ({
          documents: state.documents.map(d => d.id === id ? document : d)
        })),
        removeDocument: (id) => set((state) => ({
          documents: state.documents.filter(d => d.id !== id)
        })),

        // Chat session actions
        setChatSessions: (sessions) => set({ chatSessions: sessions }),
        addChatSession: (session) => set((state) => ({ 
          chatSessions: [...state.chatSessions, session] 
        })),
        updateChatSession: (id, session) => set((state) => ({
          chatSessions: state.chatSessions.map(s => s.id === id ? session : s)
        })),
        removeChatSession: (id) => set((state) => ({
          chatSessions: state.chatSessions.filter(s => s.id !== id),
          currentSession: state.currentSession?.id === id ? null : state.currentSession
        })),
        setCurrentSession: (session) => set({ currentSession: session }),

        // General actions
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        clearError: () => set({ error: null }),
      }),
      {
        name: 'rag-app-store',
        partialize: (state) => ({
          currentProfile: state.currentProfile,
          currentSession: state.currentSession,
        }),
      }
    ),
    {
      name: 'rag-app-store',
    }
  )
)

// Chat Store
interface ChatState {
  // State
  sessions: ChatSession[]
  currentSession: ChatSession | null
  isConnected: boolean
  isTyping: boolean
  typingUsers: Set<string>
  
  // Actions
  setSessions: (sessions: ChatSession[]) => void
  addSession: (session: ChatSession) => void
  updateSession: (id: string, session: ChatSession) => void
  removeSession: (id: string) => void
  setCurrentSession: (session: ChatSession | null) => void
  
  setConnected: (connected: boolean) => void
  setTyping: (typing: boolean) => void
  setTypingUsers: (users: Set<string>) => void
  addTypingUser: (userId: string) => void
  removeTypingUser: (userId: string) => void
}

export const useChatStore = create<ChatState>()(
  devtools(
    (set) => ({
      // Initial state
      sessions: [],
      currentSession: null,
      isConnected: false,
      isTyping: false,
      typingUsers: new Set(),

      // Session actions
      setSessions: (sessions) => set({ sessions }),
      addSession: (session) => set((state) => ({ 
        sessions: [...state.sessions, session] 
      })),
      updateSession: (id, session) => set((state) => ({
        sessions: state.sessions.map(s => s.id === id ? session : s)
      })),
      removeSession: (id) => set((state) => ({
        sessions: state.sessions.filter(s => s.id !== id),
        currentSession: state.currentSession?.id === id ? null : state.currentSession
      })),
      setCurrentSession: (session) => set({ currentSession: session }),

      // Connection actions
      setConnected: (connected) => set({ isConnected: connected }),
      setTyping: (typing) => set({ isTyping: typing }),
      setTypingUsers: (users) => set({ typingUsers: users }),
      addTypingUser: (userId) => set((state) => {
        const newUsers = new Set(state.typingUsers)
        newUsers.add(userId)
        return { typingUsers: newUsers }
      }),
      removeTypingUser: (userId) => set((state) => {
        const newUsers = new Set(state.typingUsers)
        newUsers.delete(userId)
        return { typingUsers: newUsers }
      }),
    }),
    {
      name: 'rag-chat-store',
    }
  )
)

// Document Store
interface DocumentState {
  // State
  documents: Document[]
  uploadProgress: Map<string, number>
  searchResults: any[]
  isLoading: boolean
  error: string | null
  
  // Actions
  setDocuments: (documents: Document[]) => void
  addDocument: (document: Document) => void
  updateDocument: (id: string, document: Document) => void
  removeDocument: (id: string) => void
  
  setUploadProgress: (fileId: string, progress: number) => void
  removeUploadProgress: (fileId: string) => void
  
  setSearchResults: (results: any[]) => void
  clearSearchResults: () => void
  
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useDocumentStore = create<DocumentState>()(
  devtools(
    (set) => ({
      // Initial state
      documents: [],
      uploadProgress: new Map(),
      searchResults: [],
      isLoading: false,
      error: null,

      // Document actions
      setDocuments: (documents) => set({ documents }),
      addDocument: (document) => set((state) => ({ 
        documents: [...state.documents, document] 
      })),
      updateDocument: (id, document) => set((state) => ({
        documents: state.documents.map(d => d.id === id ? document : d)
      })),
      removeDocument: (id) => set((state) => ({
        documents: state.documents.filter(d => d.id !== id)
      })),

      // Upload progress actions
      setUploadProgress: (fileId, progress) => set((state) => {
        const newProgress = new Map(state.uploadProgress)
        newProgress.set(fileId, progress)
        return { uploadProgress: newProgress }
      }),
      removeUploadProgress: (fileId) => set((state) => {
        const newProgress = new Map(state.uploadProgress)
        newProgress.delete(fileId)
        return { uploadProgress: newProgress }
      }),

      // Search actions
      setSearchResults: (results) => set({ searchResults: results }),
      clearSearchResults: () => set({ searchResults: [] }),

      // General actions
      setLoading: (loading) => set({ isLoading: loading }),
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),
    }),
    {
      name: 'rag-document-store',
    }
  )
)

// Profile Store
interface ProfileState {
  // State
  profiles: Profile[]
  currentProfile: Profile | null
  availableProviders: any
  isLoading: boolean
  error: string | null
  
  // Actions
  setProfiles: (profiles: Profile[]) => void
  addProfile: (profile: Profile) => void
  updateProfile: (id: number, profile: Profile) => void
  removeProfile: (id: number) => void
  setCurrentProfile: (profile: Profile | null) => void
  
  setAvailableProviders: (providers: any) => void
  
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useProfileStore = create<ProfileState>()(
  devtools(
    persist(
      (set) => ({
        // Initial state
        profiles: [],
        currentProfile: null,
        availableProviders: null,
        isLoading: false,
        error: null,

        // Profile actions
        setProfiles: (profiles) => set({ profiles }),
        addProfile: (profile) => set((state) => ({ 
          profiles: [...state.profiles, profile] 
        })),
        updateProfile: (id, profile) => set((state) => ({
          profiles: state.profiles.map(p => p.id === id ? profile : p)
        })),
        removeProfile: (id) => set((state) => ({
          profiles: state.profiles.filter(p => p.id !== id),
          currentProfile: state.currentProfile?.id === id ? null : state.currentProfile
        })),
        setCurrentProfile: (profile) => set({ currentProfile: profile }),

        // Provider actions
        setAvailableProviders: (providers) => set({ availableProviders: providers }),

        // General actions
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        clearError: () => set({ error: null }),
      }),
      {
        name: 'rag-profile-store',
        partialize: (state) => ({
          currentProfile: state.currentProfile,
        }),
      }
    ),
    {
      name: 'rag-profile-store',
    }
  )
)
