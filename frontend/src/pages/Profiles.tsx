import React, { useEffect, useState } from 'react'
import { Plus, Bot, Zap, Users, Settings, MessageSquare } from 'lucide-react'
import { useAppStore, useProfileStore } from '../store'
import { apiService } from '../services/api'
import ProfileList from '../components/Profiles/ProfileList'
import Button from '../components/Common/Button'
import toast from 'react-hot-toast'

const Profiles: React.FC = () => {
  const { currentProfile, setCurrentProfile } = useAppStore()
  const { profiles, setProfiles } = useProfileStore()
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    // Load profiles if not already loaded
    const loadProfiles = async () => {
      try {
        const response = await apiService.getProfiles()
        setProfiles(response.profiles)
        
        // Set first profile as current if none selected
        if (!currentProfile && response.profiles.length > 0) {
          setCurrentProfile(response.profiles[0])
        }
      } catch (error) {
        console.error('Failed to load profiles:', error)
        toast.error('Failed to load profiles')
      }
    }

    loadProfiles()
  }, [setProfiles, currentProfile, setCurrentProfile])

  // Load profile statistics
  useEffect(() => {
    const loadStats = async () => {
      if (!currentProfile) return
      
      try {
        const profileStats = await apiService.getProfileStats(currentProfile.id)
        setStats(profileStats)
      } catch (error) {
        console.error('Failed to load profile stats:', error)
      }
    }

    loadStats()
  }, [currentProfile])

  const createGeminiProfile = async () => {
    try {
      const geminiProfile = {
        name: 'Gemini Assistant',
        description: 'AI assistant powered by Google Gemini',
        prompt: 'You are a helpful AI assistant powered by Google Gemini. Use the following context to provide accurate, helpful, and detailed answers.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:',
        provider: 'google',
        model: 'gemini-1.5-pro',
        settings: {
          max_context_chunks: 6,
          chunk_size: 1200,
          chunk_overlap: 200,
          temperature: 0.7,
          max_tokens: 2000,
          top_p: 0.9,
          frequency_penalty: 0.0,
          presence_penalty: 0.0
        }
      }

      const newProfile = await apiService.createProfile(geminiProfile)
      setProfiles([...profiles, newProfile])
      setCurrentProfile(newProfile)
      toast.success('Gemini profile created successfully!')
    } catch (error: any) {
      toast.error('Failed to create Gemini profile')
    }
  }

  const providerCounts = profiles.reduce((acc, profile) => {
    acc[profile.provider] = (acc[profile.provider] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI Profiles</h1>
          <p className="text-gray-600 mt-1">
            Manage your AI assistant personalities and configurations.
          </p>
        </div>
        
        <div className="flex space-x-2">
          <Button
            onClick={createGeminiProfile}
            variant="secondary"
            size="sm"
          >
            <Bot className="w-4 h-4 mr-2" />
            Quick Gemini Profile
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      {profiles.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center">
              <Users className="w-8 h-8 text-blue-600 mr-3" />
              <div>
                <div className="text-2xl font-bold text-gray-900">{profiles.length}</div>
                <div className="text-sm text-gray-500">Total Profiles</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center">
              <Bot className="w-8 h-8 text-green-600 mr-3" />
              <div>
                <div className="text-2xl font-bold text-gray-900">{providerCounts.google || 0}</div>
                <div className="text-sm text-gray-500">Gemini Profiles</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center">
              <Zap className="w-8 h-8 text-purple-600 mr-3" />
              <div>
                <div className="text-2xl font-bold text-gray-900">{providerCounts.openai || 0}</div>
                <div className="text-sm text-gray-500">OpenAI Profiles</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center">
              <Bot className="w-8 h-8 text-orange-600 mr-3" />
              <div>
                <div className="text-2xl font-bold text-gray-900">{providerCounts.anthropic || 0}</div>
                <div className="text-sm text-gray-500">Claude Profiles</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Current Profile Info */}
      {currentProfile && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  Active Profile: {currentProfile.name}
                </h3>
                <p className="text-sm text-gray-600">
                  {currentProfile.description || 'No description'}
                </p>
                <div className="flex items-center space-x-4 mt-2">
                  <span className="text-xs text-gray-500">
                    Provider: <span className="font-medium">{currentProfile.provider}</span>
                  </span>
                  <span className="text-xs text-gray-500">
                    Model: <span className="font-medium">{currentProfile.model}</span>
                  </span>
                </div>
              </div>
            </div>
            
            {stats && (
              <div className="text-right">
                <div className="text-sm text-gray-600">
                  <div>{stats.document_count || 0} documents</div>
                  <div>{stats.chat_sessions || 0} chat sessions</div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Profile List */}
      <ProfileList />

      {/* Getting Started Guide */}
      {profiles.length === 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div className="text-center">
            <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-900 mb-2">
              Welcome to AI Profiles
            </h3>
            <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
              AI Profiles let you create different AI personalities for various tasks. 
              Each profile can use different AI providers (like Gemini, OpenAI, or Claude) 
              with custom prompts and settings.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Bot className="w-6 h-6 text-blue-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-2">Choose AI Provider</h4>
                <p className="text-sm text-gray-600">
                  Select from Gemini, OpenAI, Claude, or custom providers
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <MessageSquare className="w-6 h-6 text-green-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-2">Customize Behavior</h4>
                <p className="text-sm text-gray-600">
                  Define how your AI assistant should respond and behave
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Settings className="w-6 h-6 text-purple-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-2">Fine-tune Settings</h4>
                <p className="text-sm text-gray-600">
                  Adjust context size, temperature, and other AI parameters
                </p>
              </div>
            </div>
            
            <Button onClick={createGeminiProfile} size="lg">
              <Plus className="w-5 h-5 mr-2" />
              Create Your First Gemini Profile
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}

export default Profiles
