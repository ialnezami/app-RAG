import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout/Layout'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Documents from './pages/Documents'
import Profiles from './pages/Profiles'
import Settings from './pages/Settings'
import { useWebSocket } from './hooks/useWebSocket'
import { useApi } from './hooks/useApi'

function App() {
  const { isConnected: wsConnected } = useWebSocket()
  const { isConnected: apiConnected } = useApi()

  return (
    <div className="min-h-screen bg-gray-50">
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/chat/:sessionId" element={<Chat />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/profiles" element={<Profiles />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
      
      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10B981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#EF4444',
              secondary: '#fff',
            },
          },
        }}
      />
      
      {/* Connection status indicator */}
      <div className="fixed bottom-4 right-4 z-50">
        <div className="flex items-center space-x-2 rounded-lg bg-white px-3 py-2 shadow-lg border border-gray-200">
          <div className={`h-2 w-2 rounded-full ${
            apiConnected ? 'bg-green-500' : 'bg-red-500'
          }`} />
          <span className="text-xs text-gray-600">
            API {apiConnected ? 'Connected' : 'Disconnected'}
          </span>
          <div className={`h-2 w-2 rounded-full ${
            wsConnected ? 'bg-green-500' : 'bg-red-500'
          }`} />
          <span className="text-xs text-gray-600">
            WS {wsConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default App
