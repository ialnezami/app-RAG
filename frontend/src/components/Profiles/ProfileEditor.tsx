import React, { useState, useEffect } from 'react'
import {
  Save,
  Bot,
  HelpCircle,
  Zap,
  Brain,
  MessageSquare,
  Sliders,
  User,
  RefreshCw
} from 'lucide-react'
import { Profile, CreateProfileRequest } from '../../services/types'
import { apiService } from '../../services/api'
import Button from '../Common/Button'
import Input from '../Common/Input'
import toast from 'react-hot-toast'

interface ProfileEditorProps {
  profile?: Profile | null
  onSave: (profile: Profile) => void
  onCancel: () => void
}

interface FormData {
  name: string
  description: string
  prompt: string
  provider: string
  model: string
  settings: {
    max_context_chunks: number
    chunk_size: number
    chunk_overlap: number
    temperature: number
    max_tokens: number
    top_p: number
    frequency_penalty: number
    presence_penalty: number
  }
}

interface ProviderConfig {
  [key: string]: {
    name: string
    models: { [key: string]: { name: string; max_tokens: number } }
  }
}

const ProfileEditor: React.FC<ProfileEditorProps> = ({ profile, onSave, onCancel }) => {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    prompt: '',
    provider: 'google',
    model: 'gemini-1.5-pro',
    settings: {
      max_context_chunks: 5,
      chunk_size: 1000,
      chunk_overlap: 200,
      temperature: 0.7,
      max_tokens: 1000,
      top_p: 1.0,
      frequency_penalty: 0.0,
      presence_penalty: 0.0
    }
  })

  const [availableProviders, setAvailableProviders] = useState<ProviderConfig>({
    google: {
      name: 'Google Gemini',
      models: {
        'gemini-1.5-pro': { name: 'Gemini 1.5 Pro', max_tokens: 4000 },
        'gemini-1.5-flash': { name: 'Gemini 1.5 Flash', max_tokens: 4000 }
      }
    },
    openai: {
      name: 'OpenAI',
      models: {
        'gpt-4o-mini': { name: 'GPT-4o Mini', max_tokens: 4000 },
        'gpt-4': { name: 'GPT-4', max_tokens: 8000 },
        'gpt-3.5-turbo': { name: 'GPT-3.5 Turbo', max_tokens: 4000 }
      }
    },
    anthropic: {
      name: 'Anthropic',
      models: {
        'claude-3-sonnet': { name: 'Claude 3 Sonnet', max_tokens: 4000 },
        'claude-3-haiku': { name: 'Claude 3 Haiku', max_tokens: 4000 },
        'claude-3-opus': { name: 'Claude 3 Opus', max_tokens: 4000 }
      }
    }
  })
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [activeTab, setActiveTab] = useState<'basic' | 'prompt' | 'settings'>('basic')

  // Load available providers
  useEffect(() => {
    const loadProviders = async () => {
      try {
        const response = await apiService.getAvailableProviders()
        if (response.providers && Object.keys(response.providers).length > 0) {
          setAvailableProviders(response.providers as ProviderConfig)
        } else {
          // Use fallback providers
          setAvailableProviders(getFallbackProviders())
        }
      } catch (error) {
        console.error('Failed to load providers:', error)
        // Use fallback providers
        setAvailableProviders(getFallbackProviders())
      }
    }

    loadProviders()
  }, [])

  const getFallbackProviders = (): ProviderConfig => {
    return {
      google: {
        name: 'Google Gemini',
        models: {
          'gemini-1.5-pro': { name: 'Gemini 1.5 Pro', max_tokens: 4000 },
          'gemini-1.5-flash': { name: 'Gemini 1.5 Flash', max_tokens: 4000 }
        }
      },
      openai: {
        name: 'OpenAI',
        models: {
          'gpt-4o-mini': { name: 'GPT-4o Mini', max_tokens: 4000 },
          'gpt-4': { name: 'GPT-4', max_tokens: 8000 },
          'gpt-3.5-turbo': { name: 'GPT-3.5 Turbo', max_tokens: 4000 }
        }
      },
      anthropic: {
        name: 'Anthropic',
        models: {
          'claude-3-sonnet': { name: 'Claude 3 Sonnet', max_tokens: 4000 },
          'claude-3-haiku': { name: 'Claude 3 Haiku', max_tokens: 4000 },
          'claude-3-opus': { name: 'Claude 3 Opus', max_tokens: 4000 }
        }
      },
      custom: {
        name: 'Custom API',
        models: {
          'llama3': { name: 'Llama 3', max_tokens: 2000 },
          'custom-model': { name: 'Custom Model', max_tokens: 2000 }
        }
      }
    }
  }

  // Initialize form data when profile changes
  useEffect(() => {
    if (profile) {
      setFormData({
        name: profile.name,
        description: profile.description || '',
        prompt: profile.prompt,
        provider: profile.provider,
        model: profile.model,
        settings: {
          max_context_chunks: profile.settings.max_context_chunks || 5,
          chunk_size: profile.settings.chunk_size || 1000,
          chunk_overlap: profile.settings.chunk_overlap || 200,
          temperature: profile.settings.temperature || 0.7,
          max_tokens: profile.settings.max_tokens || 1000,
          top_p: profile.settings.top_p || 1.0,
          frequency_penalty: profile.settings.frequency_penalty || 0.0,
          presence_penalty: profile.settings.presence_penalty || 0.0
        }
      })
    }
  }, [profile])

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Profile name is required'
    } else if (formData.name.length < 2) {
      newErrors.name = 'Profile name must be at least 2 characters'
    }

    if (!formData.prompt.trim()) {
      newErrors.prompt = 'System prompt is required'
    } else if (formData.prompt.length < 10) {
      newErrors.prompt = 'System prompt must be at least 10 characters'
    }

    if (!formData.provider) {
      newErrors.provider = 'AI provider is required'
    }

    if (!formData.model) {
      newErrors.model = 'Model is required'
    }

    // Validate settings
    if (formData.settings.max_context_chunks < 1 || formData.settings.max_context_chunks > 20) {
      newErrors.max_context_chunks = 'Context chunks must be between 1 and 20'
    }

    if (formData.settings.chunk_size < 100 || formData.settings.chunk_size > 3000) {
      newErrors.chunk_size = 'Chunk size must be between 100 and 3000'
    }

    if (formData.settings.chunk_overlap < 0 || formData.settings.chunk_overlap >= formData.settings.chunk_size) {
      newErrors.chunk_overlap = 'Chunk overlap must be less than chunk size'
    }

    if (formData.settings.temperature < 0 || formData.settings.temperature > 2) {
      newErrors.temperature = 'Temperature must be between 0 and 2'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      toast.error('Please fix the form errors')
      return
    }

    try {
      setIsLoading(true)

      const profileData: CreateProfileRequest = {
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
        prompt: formData.prompt.trim(),
        provider: formData.provider,
        model: formData.model,
        settings: formData.settings
      }

      let savedProfile: Profile
      if (profile) {
        savedProfile = await apiService.updateProfile(profile.id, profileData)
        toast.success('Profile updated successfully')
      } else {
        savedProfile = await apiService.createProfile(profileData)
        toast.success('Profile created successfully')
      }

      onSave(savedProfile)
    } catch (error: any) {
      toast.error(error.message || 'Failed to save profile')
    } finally {
      setIsLoading(false)
    }
  }

  const handleProviderChange = (provider: string) => {
    setFormData(prev => {
      const newFormData = { ...prev, provider }
      
      // Reset to first available model for the new provider
      const providerConfig = availableProviders[provider]
      if (providerConfig && Object.keys(providerConfig.models).length > 0) {
        newFormData.model = Object.keys(providerConfig.models)[0]
      }
      
      return newFormData
    })
  }

  const getAvailableModels = () => {
    const providerConfig = availableProviders[formData.provider]
    return providerConfig ? providerConfig.models : {}
  }

  const getPromptTemplates = () => {
    return {
      general: "You are a helpful assistant. Use the following context to answer questions accurately and concisely.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:",
      technical: "You are a technical expert. Provide detailed, accurate answers based on the documentation context. Include code examples when relevant.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:",
      creative: "You are a creative writer. Use the provided context to inspire creative and engaging responses.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:",
      analytical: "You are a data analyst. Analyze the provided context and provide insights, patterns, and actionable recommendations.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:",
      educational: "You are an educational tutor. Explain concepts clearly using the provided context, break down complex topics, and provide examples.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:"
    }
  }

  const applyPromptTemplate = (template: string) => {
    const templates = getPromptTemplates()
    setFormData(prev => ({ ...prev, prompt: templates[template as keyof typeof templates] }))
  }

  const tabs = [
    { id: 'basic', label: 'Basic Info', icon: User },
    { id: 'prompt', label: 'System Prompt', icon: MessageSquare },
    { id: 'settings', label: 'AI Settings', icon: Sliders }
  ]

  return (
    <div className="max-h-[80vh] overflow-y-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Tab Navigation */}
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id as any)}
                className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <tab.icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Basic Info Tab */}
        {activeTab === 'basic' && (
          <div className="space-y-6 p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Profile Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Profile Name *
                </label>
                <Input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Technical Expert"
                  error={errors.name}
                  required
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <Input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Brief description of this profile's purpose"
                />
              </div>
            </div>

            {/* AI Provider Selection */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  AI Provider *
                </label>
                <select
                  value={formData.provider}
                  onChange={(e) => handleProviderChange(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  {Object.entries(availableProviders).map(([key, config]) => (
                    <option key={key} value={key}>
                      {config.name}
                    </option>
                  ))}
                </select>
                {errors.provider && (
                  <p className="mt-1 text-sm text-red-600">{errors.provider}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model *
                </label>
                <select
                  value={formData.model}
                  onChange={(e) => setFormData(prev => ({ ...prev, model: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                >
                  {Object.entries(getAvailableModels()).map(([key, config]) => (
                    <option key={key} value={key}>
                      {config.name}
                    </option>
                  ))}
                </select>
                {errors.model && (
                  <p className="mt-1 text-sm text-red-600">{errors.model}</p>
                )}
              </div>
            </div>

            {/* Provider Info */}
            {formData.provider && (
              <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                <div className="flex items-center">
                  <Bot className="w-5 h-5 text-blue-600 mr-2" />
                  <div>
                    <h4 className="text-sm font-medium text-blue-900">
                      {availableProviders[formData.provider]?.name || formData.provider}
                    </h4>
                    <p className="text-xs text-blue-700">
                      Model: {getAvailableModels()[formData.model]?.name || formData.model}
        </p>
      </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* System Prompt Tab */}
        {activeTab === 'prompt' && (
          <div className="space-y-6 p-6">
            {/* Prompt Templates */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quick Templates
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {Object.entries(getPromptTemplates()).map(([key]) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => applyPromptTemplate(key)}
                    className="px-3 py-2 text-xs border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                  >
                    {key.charAt(0).toUpperCase() + key.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* System Prompt */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                System Prompt *
              </label>
              <textarea
                value={formData.prompt}
                onChange={(e) => setFormData(prev => ({ ...prev, prompt: e.target.value }))}
                rows={8}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
                placeholder="Define how the AI should behave and respond to questions..."
                required
              />
              {errors.prompt && (
                <p className="mt-1 text-sm text-red-600">{errors.prompt}</p>
              )}
              
              <div className="mt-2 text-xs text-gray-500">
                <p><strong>Available variables:</strong></p>
                <ul className="list-disc list-inside mt-1 space-y-1">
                  <li><code className="bg-gray-100 px-1 rounded">{'{context}'}</code> - Retrieved document context</li>
                  <li><code className="bg-gray-100 px-1 rounded">{'{question}'}</code> - User's question</li>
                </ul>
              </div>
            </div>

            {/* Prompt Preview */}
            <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Preview</h4>
              <div className="text-xs text-gray-600 whitespace-pre-wrap font-mono">
                {formData.prompt.slice(0, 200)}
                {formData.prompt.length > 200 && '...'}
              </div>
            </div>
          </div>
        )}

        {/* AI Settings Tab */}
        {activeTab === 'settings' && (
          <div className="space-y-6 p-6">
            {/* Context Settings */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <Brain className="w-5 h-5 mr-2" />
                Context Settings
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Context Chunks
                    <HelpCircle className="w-4 h-4 text-gray-400 ml-1 inline" />
                  </label>
                  <Input
                    type="number"
                    min="1"
                    max="20"
                    value={formData.settings.max_context_chunks}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      settings: { ...prev.settings, max_context_chunks: parseInt(e.target.value) }
                    }))}
                    error={errors.max_context_chunks}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Chunk Size
                    <HelpCircle className="w-4 h-4 text-gray-400 ml-1 inline" />
                  </label>
                  <Input
                    type="number"
                    min="100"
                    max="3000"
                    step="100"
                    value={formData.settings.chunk_size}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      settings: { ...prev.settings, chunk_size: parseInt(e.target.value) }
                    }))}
                    error={errors.chunk_size}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Chunk Overlap
                    <HelpCircle className="w-4 h-4 text-gray-400 ml-1 inline" />
                  </label>
                  <Input
                    type="number"
                    min="0"
                    max="500"
                    step="50"
                    value={formData.settings.chunk_overlap}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      settings: { ...prev.settings, chunk_overlap: parseInt(e.target.value) }
                    }))}
                    error={errors.chunk_overlap}
                  />
                </div>
              </div>
            </div>

            {/* AI Model Settings */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
                <Zap className="w-5 h-5 mr-2" />
                AI Model Settings
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Temperature
                    <HelpCircle className="w-4 h-4 text-gray-400 ml-1 inline" />
                  </label>
                  <div className="space-y-2">
                    <input
                      type="range"
                      min="0"
                      max="2"
                      step="0.1"
                      value={formData.settings.temperature}
                      onChange={(e) => setFormData(prev => ({
                        ...prev,
                        settings: { ...prev.settings, temperature: parseFloat(e.target.value) }
                      }))}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>Focused (0)</span>
                      <span className="font-medium">{formData.settings.temperature}</span>
                      <span>Creative (2)</span>
                    </div>
                  </div>
                  {errors.temperature && (
                    <p className="mt-1 text-sm text-red-600">{errors.temperature}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Tokens
                    <HelpCircle className="w-4 h-4 text-gray-400 ml-1 inline" />
                  </label>
                  <Input
                    type="number"
                    min="100"
                    max="4000"
                    step="100"
                    value={formData.settings.max_tokens}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      settings: { ...prev.settings, max_tokens: parseInt(e.target.value) }
                    }))}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Top P
                    <HelpCircle className="w-4 h-4 text-gray-400 ml-1 inline" />
                  </label>
                  <Input
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={formData.settings.top_p}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      settings: { ...prev.settings, top_p: parseFloat(e.target.value) }
                    }))}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Frequency Penalty
                    <HelpCircle className="w-4 h-4 text-gray-400 ml-1 inline" />
                  </label>
                  <Input
                    type="number"
                    min="-2"
                    max="2"
                    step="0.1"
                    value={formData.settings.frequency_penalty}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      settings: { ...prev.settings, frequency_penalty: parseFloat(e.target.value) }
                    }))}
                  />
                </div>
              </div>
            </div>

            {/* Settings Preview */}
            <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Configuration Summary</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                <div>
                  <span className="text-gray-500">Context:</span>
                  <span className="ml-1 font-medium">{formData.settings.max_context_chunks} chunks</span>
                </div>
                <div>
                  <span className="text-gray-500">Chunk Size:</span>
                  <span className="ml-1 font-medium">{formData.settings.chunk_size} chars</span>
                </div>
                <div>
                  <span className="text-gray-500">Temperature:</span>
                  <span className="ml-1 font-medium">{formData.settings.temperature}</span>
                </div>
                <div>
                  <span className="text-gray-500">Max Tokens:</span>
                  <span className="ml-1 font-medium">{formData.settings.max_tokens}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Form Actions */}
        <div className="flex justify-end space-x-3 px-6 py-4 bg-gray-50 border-t border-gray-200">
          <Button
            type="button"
            onClick={onCancel}
            variant="secondary"
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={isLoading}
            className="min-w-[100px]"
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                {profile ? 'Update' : 'Create'} Profile
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  )
}

export default ProfileEditor
