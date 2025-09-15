import React from 'react'
import DocumentList from '../components/Documents/DocumentList'
import DocumentUpload from '../components/Documents/DocumentUpload'

const Documents: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
      </div>
      
      <DocumentUpload />
      <DocumentList />
    </div>
  )
}

export default Documents
