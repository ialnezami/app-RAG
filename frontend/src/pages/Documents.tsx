import React, { useEffect } from 'react'
import { useAppStore } from '../store'
import { apiService } from '../services/api'
import DocumentList from '../components/Documents/DocumentList'
import DocumentUpload from '../components/Documents/DocumentUpload'
import ProfileSelector from '../components/Profiles/ProfileSelector'

const Documents: React.FC = () => {
  const { profiles, setProfiles } = useAppStore()

  useEffect(() => {
    // Load profiles if not already loaded
    const loadProfiles = async () => {
      try {
        const response = await apiService.getProfiles()
        setProfiles(response.profiles)
      } catch (error) {
        console.error('Failed to load profiles:', error)
      }
    }

    if (profiles.length === 0) {
      loadProfiles()
    }
  }, [profiles.length, setProfiles])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
        <p className="text-gray-600 mt-1">
          Manage your document library and upload new files for AI analysis.
        </p>
      </div>

      {/* Profile Selection */}
      {profiles.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-900">
              Select Profile for Document Management
            </h3>
            <div className="w-64">
              <ProfileSelector />
            </div>
          </div>
        </div>
      )}
      
      {/* Upload Section */}
      <DocumentUpload />
      
      {/* Document List */}
      <DocumentList />
    </div>
  )
}

export default Documents
