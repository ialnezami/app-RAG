import React, { useState, useEffect, useCallback } from 'react'
import {
  User,
  Edit3,
  Trash2,
  Plus,
  Search,
  RefreshCw,
  Star,
  Copy,
  MoreVertical,
  Bot,
  AlertCircle
} from 'lucide-react'
import { useAppStore, useProfileStore } from '../../store'
import { apiService } from '../../services/api'
import { Profile } from '../../services/types'
import Button from '../Common/Button'
import Modal from '../Common/Modal'
import ProfileEditor from './ProfileEditor'
import toast from 'react-hot-toast'

interface ProfileListProps {
  onEditProfile?: (profile: Profile) => void
  onSelectProfile?: (profile: Profile) => void
  showActions?: boolean
}

const ProfileList: React.FC<ProfileListProps> = ({ 
  onEditProfile, 
  onSelectProfile,
  showActions = true 
}) => {
  const { currentProfile, setCurrentProfile } = useAppStore()
  const { 
    profiles, 
    setProfiles, 
    addProfile, 
    updateProfile, 
    removeProfile, 
    isLoading, 
    setLoading, 
    error, 
    setError 
  } = useProfileStore()
  
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedProfile, setSelectedProfile] = useState<Profile | null>(null)
  const [showEditor, setShowEditor] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [profileToDelete, setProfileToDelete] = useState<Profile | null>(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [filterByProvider, setFilterByProvider] = useState<string>('all')

  const loadProfiles = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await apiService.getProfiles()
      setProfiles(response.profiles)
    } catch (error: any) {
      setError(error.message || 'Failed to load profiles')
      toast.error('Failed to load profiles')
    } finally {
      setLoading(false)
    }
  }, [setProfiles, setLoading, setError])

  useEffect(() => {
    loadProfiles()
  }, [loadProfiles])

  const handleEditProfile = (profile: Profile) => {
    setSelectedProfile(profile)
    setShowEditor(true)
    onEditProfile?.(profile)
  }

  const handleDeleteProfile = async (profile: Profile) => {
    try {
      await apiService.deleteProfile(profile.id)
      removeProfile(profile.id)
      
      // If this was the current profile, clear it
      if (currentProfile?.id === profile.id) {
        setCurrentProfile(null)
      }
      
      setShowDeleteModal(false)
      setProfileToDelete(null)
      toast.success('Profile deleted successfully')
    } catch (error: any) {
      toast.error('Failed to delete profile')
    }
  }

  const handleSelectProfile = (profile: Profile) => {
    setCurrentProfile(profile)
    onSelectProfile?.(profile)
    toast.success(`Selected profile: ${profile.name}`)
  }

  const handleDuplicateProfile = async (profile: Profile) => {
    try {
      const duplicatedProfile = {
        name: `${profile.name} (Copy)`,
        description: profile.description,
        prompt: profile.prompt,
        provider: profile.provider,
        model: profile.model,
        settings: { ...profile.settings }
      }
      
      const newProfile = await apiService.createProfile(duplicatedProfile)
      addProfile(newProfile)
      toast.success('Profile duplicated successfully')
    } catch (error: any) {
      toast.error('Failed to duplicate profile')
    }
  }

  const handleCreateProfile = () => {
    setSelectedProfile(null)
    setShowCreateModal(true)
  }

  const handleProfileSaved = (profile: Profile) => {
    if (selectedProfile) {
      updateProfile(profile.id, profile)
    } else {
      addProfile(profile)
    }
    setShowEditor(false)
    setShowCreateModal(false)
    setSelectedProfile(null)
  }

  const getProviderIcon = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'openai':
        return <Bot className="w-5 h-5 text-green-600" />
      case 'anthropic':
        return <Bot className="w-5 h-5 text-purple-600" />
      case 'google':
        return <Bot className="w-5 h-5 text-blue-600" />
      case 'custom':
        return <Bot className="w-5 h-5 text-gray-600" />
      default:
        return <Bot className="w-5 h-5 text-gray-400" />
    }
  }

  const getProviderBadgeColor = (provider: string) => {
    switch (provider.toLowerCase()) {
      case 'openai':
        return 'bg-green-100 text-green-800'
      case 'anthropic':
        return 'bg-purple-100 text-purple-800'
      case 'google':
        return 'bg-blue-100 text-blue-800'
      case 'custom':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const filteredProfiles = profiles
    .filter(profile => {
      const matchesSearch = profile.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (profile.description || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                           profile.model.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesProvider = filterByProvider === 'all' || profile.provider === filterByProvider
      
      return matchesSearch && matchesProvider
    })

  const availableProviders = Array.from(new Set(profiles.map(p => p.provider)))

  return (
    <>
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-medium text-gray-900">
                AI Profiles
              </h2>
              <p className="text-sm text-gray-500">
                {profiles.length} profiles • {currentProfile ? `Active: ${currentProfile.name}` : 'No profile selected'}
              </p>
            </div>
            <div className="flex space-x-2">
              <Button
                onClick={loadProfiles}
                variant="secondary"
                size="sm"
                disabled={isLoading}
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              {showActions && (
                <Button
                  onClick={handleCreateProfile}
                  size="sm"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  New Profile
                </Button>
              )}
            </div>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search profiles..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <select
              value={filterByProvider}
              onChange={(e) => setFilterByProvider(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Providers</option>
              {availableProviders.map(provider => (
                <option key={provider} value={provider}>
                  {provider.charAt(0).toUpperCase() + provider.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Error State */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="flex">
                <AlertCircle className="w-5 h-5 text-red-400 mr-2 mt-0.5" />
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="text-center py-8">
              <RefreshCw className="w-8 h-8 text-gray-400 mx-auto mb-4 animate-spin" />
              <p className="text-gray-600">Loading profiles...</p>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && filteredProfiles.length === 0 && (
            <div className="text-center py-8">
              <User className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {searchTerm ? 'No profiles found' : 'No profiles created'}
              </h3>
              <p className="text-gray-600 mb-4">
                {searchTerm 
                  ? 'Try adjusting your search terms or filters.'
                  : 'Create your first AI profile to get started with personalized assistance.'
                }
              </p>
              {showActions && !searchTerm && (
                <Button onClick={handleCreateProfile}>
                  <Plus className="w-4 h-4 mr-2" />
                  Create First Profile
                </Button>
              )}
            </div>
          )}

          {/* Profile Grid */}
          {!isLoading && filteredProfiles.length > 0 && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filteredProfiles.map((profile) => (
                <div
                  key={profile.id}
                  className={`border rounded-lg p-4 hover:shadow-md transition-all cursor-pointer ${
                    currentProfile?.id === profile.id
                      ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleSelectProfile(profile)}
                >
                  {/* Profile Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      {getProviderIcon(profile.provider)}
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-gray-900 truncate flex items-center">
                          {profile.name}
                          {currentProfile?.id === profile.id && (
                            <Star className="w-4 h-4 text-yellow-500 ml-2 fill-current" />
                          )}
                        </h3>
                        <p className="text-xs text-gray-500 truncate">
                          {profile.description || 'No description'}
                        </p>
                      </div>
                    </div>
                    
                    {showActions && (
                      <div className="relative">
                        <button 
                          className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Provider Badge */}
                  <div className="mb-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getProviderBadgeColor(profile.provider)}`}>
                      {profile.provider.charAt(0).toUpperCase() + profile.provider.slice(1)}
                    </span>
                    <span className="ml-2 text-xs text-gray-500">
                      {profile.model}
                    </span>
                  </div>

                  {/* Profile Settings Preview */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Context Chunks:</span>
                      <span className="font-medium">{profile.settings.max_context_chunks || 5}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Chunk Size:</span>
                      <span className="font-medium">{profile.settings.chunk_size || 1000}</span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>Temperature:</span>
                      <span className="font-medium">{profile.settings.temperature || 0.7}</span>
                    </div>
                  </div>

                  {/* Profile Actions */}
                  {showActions && (
                    <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                      <div className="flex space-x-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleEditProfile(profile)
                          }}
                          className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                          title="Edit Profile"
                        >
                          <Edit3 className="w-4 h-4" />
                        </button>
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDuplicateProfile(profile)
                          }}
                          className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                          title="Duplicate Profile"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>

                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          setProfileToDelete(profile)
                          setShowDeleteModal(true)
                        }}
                        className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                        title="Delete Profile"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Profile Statistics */}
          {!isLoading && profiles.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{profiles.length}</div>
                  <div className="text-xs text-gray-500">Total Profiles</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {availableProviders.length}
                  </div>
                  <div className="text-xs text-gray-500">Providers</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {profiles.filter(p => p.provider === 'google').length}
                  </div>
                  <div className="text-xs text-gray-500">Gemini Profiles</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {currentProfile ? '1' : '0'}
                  </div>
                  <div className="text-xs text-gray-500">Active</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Profile Editor Modal */}
      <Modal
        isOpen={showEditor || showCreateModal}
        onClose={() => {
          setShowEditor(false)
          setShowCreateModal(false)
          setSelectedProfile(null)
        }}
        title={selectedProfile ? 'Edit Profile' : 'Create New Profile'}
      >
        <ProfileEditor
          profile={selectedProfile}
          onSave={handleProfileSaved}
          onCancel={() => {
            setShowEditor(false)
            setShowCreateModal(false)
            setSelectedProfile(null)
          }}
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete Profile"
      >
        <div className="p-6">
          <div className="flex items-center mb-4">
            <AlertCircle className="w-6 h-6 text-red-500 mr-3" />
            <h3 className="text-lg font-medium text-gray-900">
              Are you sure?
            </h3>
          </div>
          
          <p className="text-gray-600 mb-4">
            This will permanently delete the profile "{profileToDelete?.name}" and all its associated documents and chat sessions.
          </p>
          
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 mb-6">
            <div className="flex">
              <AlertCircle className="w-5 h-5 text-yellow-400 mr-2 mt-0.5" />
              <p className="text-yellow-800 text-sm">
                <strong>Warning:</strong> This action cannot be undone and will remove all documents, 
                embeddings, and chat history associated with this profile.
              </p>
            </div>
          </div>
          
          <div className="flex justify-end space-x-3">
            <Button
              onClick={() => setShowDeleteModal(false)}
              variant="secondary"
            >
              Cancel
            </Button>
            <Button
              onClick={() => profileToDelete && handleDeleteProfile(profileToDelete)}
              variant="primary"
              className="bg-red-600 hover:bg-red-700"
            >
              Delete Profile
            </Button>
          </div>
        </div>
      </Modal>
    </>
  )
}

export default ProfileList
