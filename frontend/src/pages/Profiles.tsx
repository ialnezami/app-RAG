import React from 'react'
import ProfileList from '../components/Profiles/ProfileList'
import ProfileEditor from '../components/Profiles/ProfileEditor'

const Profiles: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">AI Profiles</h1>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ProfileList />
        </div>
        <div className="lg:col-span-1">
          <ProfileEditor />
        </div>
      </div>
    </div>
  )
}

export default Profiles
