import React, { useState, useEffect, useCallback } from 'react'
import { 
  FileText, 
  Download, 
  Trash2, 
  Search, 
  Filter, 
  RefreshCw, 
  Eye,
  Calendar,
  HardDrive,
  CheckCircle,
  Clock,
  AlertCircle,
  MoreVertical
} from 'lucide-react'
import { useAppStore, useDocumentStore } from '../../store'
import { apiService } from '../../services/api'
import { Document } from '../../services/types'
import Button from '../Common/Button'
import Modal from '../Common/Modal'
import DocumentViewer from './DocumentViewer'
import toast from 'react-hot-toast'

const DocumentList: React.FC = () => {
  const { currentProfile } = useAppStore()
  const { documents, setDocuments, removeDocument, isLoading, setLoading, error, setError } = useDocumentStore()
  
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null)
  const [showViewer, setShowViewer] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [documentToDelete, setDocumentToDelete] = useState<Document | null>(null)
  const [sortBy, setSortBy] = useState<'upload_date' | 'filename' | 'file_size'>('upload_date')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [filterByProcessed, setFilterByProcessed] = useState<'all' | 'processed' | 'unprocessed'>('all')
  const [page, setPage] = useState(1)
  const [totalDocuments, setTotalDocuments] = useState(0)

  const loadDocuments = useCallback(async () => {
    if (!currentProfile) return

    try {
      setLoading(true)
      setError(null)
      
      const response = await apiService.getDocuments(currentProfile.id, page, 50)
      setDocuments(response.documents)
      setTotalDocuments(response.total)
    } catch (error: any) {
      setError(error.message || 'Failed to load documents')
      toast.error('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }, [currentProfile, page, setDocuments, setLoading, setError])

  useEffect(() => {
    loadDocuments()
  }, [loadDocuments])

  const handleDeleteDocument = async (document: Document) => {
    try {
      await apiService.deleteDocument(document.id)
      removeDocument(document.id)
      setShowDeleteModal(false)
      setDocumentToDelete(null)
      toast.success('Document deleted successfully')
    } catch (error: any) {
      toast.error('Failed to delete document')
    }
  }

  const handleViewDocument = (document: Document) => {
    setSelectedDocument(document)
    setShowViewer(true)
  }

  const handleReprocessDocument = async (document: Document) => {
    try {
      if (!currentProfile) return
      await apiService.processDocument(document.id, currentProfile.id)
      toast.success('Document reprocessing started')
      // Reload documents to get updated status
      setTimeout(loadDocuments, 1000)
    } catch (error: any) {
      toast.error('Failed to start reprocessing')
    }
  }

  const filteredDocuments = documents
    .filter(doc => {
      const matchesSearch = doc.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           doc.original_filename.toLowerCase().includes(searchTerm.toLowerCase())
      
      const matchesFilter = filterByProcessed === 'all' ||
                           (filterByProcessed === 'processed' && doc.processed) ||
                           (filterByProcessed === 'unprocessed' && !doc.processed)
      
      return matchesSearch && matchesFilter
    })
    .sort((a, b) => {
      let aValue: any, bValue: any
      
      switch (sortBy) {
        case 'filename':
          aValue = a.filename.toLowerCase()
          bValue = b.filename.toLowerCase()
          break
        case 'file_size':
          aValue = a.file_size || 0
          bValue = b.file_size || 0
          break
        case 'upload_date':
        default:
          aValue = new Date(a.upload_date)
          bValue = new Date(b.upload_date)
          break
      }
      
      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0
      }
    })

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getFileTypeIcon = (mimeType: string | null) => {
    if (!mimeType) return <FileText className="w-5 h-5 text-gray-400" />
    
    if (mimeType.includes('pdf')) return <FileText className="w-5 h-5 text-red-500" />
    if (mimeType.includes('word')) return <FileText className="w-5 h-5 text-blue-500" />
    if (mimeType.includes('text')) return <FileText className="w-5 h-5 text-gray-500" />
    
    return <FileText className="w-5 h-5 text-gray-400" />
  }

  const getProcessingStatus = (processed: boolean) => {
    if (processed) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          <CheckCircle className="w-3 h-3 mr-1" />
          Processed
        </span>
      )
    } else {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          <Clock className="w-3 h-3 mr-1" />
          Processing
        </span>
      )
    }
  }

  if (!currentProfile) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Document List
          </h2>
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">
              Please select a profile to view documents.
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-medium text-gray-900">
                Document Library
              </h2>
              <p className="text-sm text-gray-500">
                Profile: {currentProfile.name} • {totalDocuments} documents
              </p>
            </div>
            <Button
              onClick={loadDocuments}
              variant="secondary"
              size="sm"
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>

          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            
            <div className="flex gap-2">
              <select
                value={filterByProcessed}
                onChange={(e) => setFilterByProcessed(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Documents</option>
                <option value="processed">Processed</option>
                <option value="unprocessed">Processing</option>
              </select>
              
              <select
                value={`${sortBy}-${sortOrder}`}
                onChange={(e) => {
                  const [field, order] = e.target.value.split('-')
                  setSortBy(field as any)
                  setSortOrder(order as any)
                }}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="upload_date-desc">Newest First</option>
                <option value="upload_date-asc">Oldest First</option>
                <option value="filename-asc">Name A-Z</option>
                <option value="filename-desc">Name Z-A</option>
                <option value="file_size-desc">Largest First</option>
                <option value="file_size-asc">Smallest First</option>
              </select>
            </div>
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
              <p className="text-gray-600">Loading documents...</p>
            </div>
          )}

          {/* Empty State */}
          {!isLoading && filteredDocuments.length === 0 && (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                {searchTerm ? 'No documents found' : 'No documents uploaded'}
              </h3>
              <p className="text-gray-600">
                {searchTerm 
                  ? 'Try adjusting your search terms or filters.'
                  : 'Upload your first document to get started with AI-powered search and chat.'
                }
              </p>
            </div>
          )}

          {/* Document Grid */}
          {!isLoading && filteredDocuments.length > 0 && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filteredDocuments.map((document) => (
                <div
                  key={document.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  {/* Document Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-3 flex-1 min-w-0">
                      {getFileTypeIcon(document.mime_type)}
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-gray-900 truncate">
                          {document.original_filename}
                        </h3>
                        <p className="text-xs text-gray-500 truncate">
                          {document.filename}
                        </p>
                      </div>
                    </div>
                    
                    <div className="relative">
                      <button className="p-1 text-gray-400 hover:text-gray-600 transition-colors">
                        <MoreVertical className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Document Status */}
                  <div className="mb-3">
                    {getProcessingStatus(document.processed)}
                  </div>

                  {/* Document Metadata */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-xs text-gray-500">
                      <Calendar className="w-3 h-3 mr-1" />
                      {formatDate(document.upload_date)}
                    </div>
                    {document.file_size && (
                      <div className="flex items-center text-xs text-gray-500">
                        <HardDrive className="w-3 h-3 mr-1" />
                        {formatFileSize(document.file_size)}
                      </div>
                    )}
                    {document.document_metadata && Object.keys(document.document_metadata).length > 0 && (
                      <div className="text-xs text-gray-500">
                        {Object.entries(document.document_metadata).slice(0, 2).map(([key, value]) => (
                          <div key={key} className="flex">
                            <span className="font-medium">{key}:</span>
                            <span className="ml-1 truncate">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Document Actions */}
                  <div className="flex items-center justify-between">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleViewDocument(document)}
                        className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                        title="View Document"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                      
                      {!document.processed && (
                        <button
                          onClick={() => handleReprocessDocument(document)}
                          className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                          title="Reprocess Document"
                        >
                          <RefreshCw className="w-4 h-4" />
                        </button>
                      )}
                    </div>

                    <button
                      onClick={() => {
                        setDocumentToDelete(document)
                        setShowDeleteModal(true)
                      }}
                      className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                      title="Delete Document"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalDocuments > 50 && (
            <div className="mt-6 flex items-center justify-between">
              <p className="text-sm text-gray-700">
                Showing {Math.min((page - 1) * 50 + 1, totalDocuments)} to{' '}
                {Math.min(page * 50, totalDocuments)} of {totalDocuments} documents
              </p>
              
              <div className="flex space-x-2">
                <Button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  variant="secondary"
                  size="sm"
                >
                  Previous
                </Button>
                <Button
                  onClick={() => setPage(p => p + 1)}
                  disabled={page * 50 >= totalDocuments}
                  variant="secondary"
                  size="sm"
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Document Viewer Modal */}
      <Modal
        isOpen={showViewer}
        onClose={() => setShowViewer(false)}
        title={selectedDocument?.original_filename || 'Document Viewer'}
        maxWidth="4xl"
      >
        {selectedDocument && (
          <DocumentViewer document={selectedDocument} />
        )}
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={showDeleteModal}
        onClose={() => setShowDeleteModal(false)}
        title="Delete Document"
      >
        <div className="p-6">
          <div className="flex items-center mb-4">
            <AlertCircle className="w-6 h-6 text-red-500 mr-3" />
            <h3 className="text-lg font-medium text-gray-900">
              Are you sure?
            </h3>
          </div>
          
          <p className="text-gray-600 mb-6">
            This will permanently delete "{documentToDelete?.original_filename}" and all its associated data. 
            This action cannot be undone.
          </p>
          
          <div className="flex justify-end space-x-3">
            <Button
              onClick={() => setShowDeleteModal(false)}
              variant="secondary"
            >
              Cancel
            </Button>
            <Button
              onClick={() => documentToDelete && handleDeleteDocument(documentToDelete)}
              variant="primary"
              className="bg-red-600 hover:bg-red-700"
            >
              Delete Document
            </Button>
          </div>
        </div>
      </Modal>
    </>
  )
}

export default DocumentList
