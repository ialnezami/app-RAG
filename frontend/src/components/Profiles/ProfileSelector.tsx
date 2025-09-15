import React, { useState } from 'react'
import { ChevronDown, Check } from 'lucide-react'
import { useAppStore } from '../../store'
import { Profile } from '../../services/types'

const ProfileSelector: React.FC = () => {
  const { profiles, currentProfile, setCurrentProfile } = useAppStore()
  const [isOpen, setIsOpen] = useState(false)

  const handleSelectProfile = (profile: Profile) => {
    setCurrentProfile(profile)
    setIsOpen(false)
  }

  if (profiles.length === 0) {
    return (
      <div className="text-sm text-gray-500">
        No profiles available
      </div>
    )
  }

  return (
    <div className="relative">
      <button
        type="button"
        className="relative w-full bg-white border border-gray-300 rounded-md shadow-sm pl-3 pr-10 py-2 text-left cursor-default focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="block truncate">
          {currentProfile ? currentProfile.name : 'Select Profile'}
        </span>
        <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
          <ChevronDown className="h-5 w-5 text-gray-400" />
        </span>
      </button>

      {isOpen && (
        <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
          {profiles.map((profile) => (
            <div
              key={profile.id}
              className="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-gray-50"
              onClick={() => handleSelectProfile(profile)}
            >
              <div className="flex items-center">
                <span className="block truncate font-normal">
                  {profile.name}
                </span>
                {currentProfile?.id === profile.id && (
                  <span className="absolute inset-y-0 right-0 flex items-center pr-4">
                    <Check className="h-5 w-5 text-primary-600" />
                  </span>
                )}
              </div>
              <div className="text-xs text-gray-500 truncate">
                {profile.provider} - {profile.model}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default ProfileSelector
