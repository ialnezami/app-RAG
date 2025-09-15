import React, { useState } from 'react'
import { FileText, Download, Eye, EyeOff, Calendar, HardDrive, Tag } from 'lucide-react'
import { Document } from '../../services/types'
import { formatDate, formatFileSize } from '../../utils'
import Button from '../Common/Button'

interface DocumentViewerProps {
  document: Document
  onClose?: () => void
  showMetadata?: boolean
  className?: string
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({
  document,
  onClose,
  showMetadata = true,
  className
}) => {
  const [showFullMetadata, setShowFullMetadata] = useState(false)

  const handleDownload = () => {
    // This would typically download the original file
    console.log('Downloading document:', document.id)
  }

  const getFileIcon = (mimeType?: string) => {
    if (!mimeType) return <FileText className="h-8 w-8" />
    
    if (mimeType.includes('pdf')) {
      return <FileText className="h-8 w-8 text-red-500" />
    } else if (mimeType.includes('word') || mimeType.includes('document')) {
      return <FileText className="h-8 w-8 text-blue-500" />
    } else if (mimeType.includes('text')) {
      return <FileText className="h-8 w-8 text-green-500" />
    }
    
    return <FileText className="h-8 w-8 text-gray-500" />
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          {getFileIcon(document.mime_type)}
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              {document.original_filename}
            </h3>
            <p className="text-sm text-gray-500">
              Uploaded {formatDate(document.upload_date)}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownload}
          >
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
          
          {onClose && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
            >
              Close
            </Button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Status */}
        <div className="flex items-center space-x-2 mb-4">
          <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            document.processed 
              ? 'bg-green-100 text-green-800' 
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {document.processed ? 'Processed' : 'Processing'}
          </div>
          
          <span className="text-sm text-gray-500">
            Profile ID: {document.profile_id}
          </span>
        </div>

        {/* Basic Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <HardDrive className="h-4 w-4" />
            <span>
              {document.file_size ? formatFileSize(document.file_size) : 'Unknown size'}
            </span>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Calendar className="h-4 w-4" />
            <span>
              {formatDate(document.upload_date)}
            </span>
          </div>
        </div>

        {/* Metadata */}
        {showMetadata && document.metadata && Object.keys(document.metadata).length > 0 && (
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-900 flex items-center">
                <Tag className="h-4 w-4 mr-2" />
                Metadata
              </h4>
              
              <button
                onClick={() => setShowFullMetadata(!showFullMetadata)}
                className="flex items-center space-x-1 text-xs text-gray-500 hover:text-gray-700"
              >
                {showFullMetadata ? (
                  <EyeOff className="h-3 w-3" />
                ) : (
                  <Eye className="h-3 w-3" />
                )}
                <span>{showFullMetadata ? 'Hide' : 'Show'} details</span>
              </button>
            </div>
            
            <div className="space-y-2">
              {Object.entries(document.metadata)
                .filter(([key]) => showFullMetadata || ['title', 'author', 'pages'].includes(key))
                .map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-600 capitalize">
                      {key.replace(/_/g, ' ')}:
                    </span>
                    <span className="text-gray-900 font-medium">
                      {String(value)}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Processing Status */}
        {!document.processed && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-yellow-600 border-t-transparent" />
              <span className="text-sm text-yellow-800">
                Document is being processed...
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentViewer
