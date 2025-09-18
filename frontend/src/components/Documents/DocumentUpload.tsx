import React, { useState, useRef, useCallback } from 'react'
import { Upload, File, X, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import { useAppStore, useDocumentStore } from '../../store'
import { apiService } from '../../services/api'
import Button from '../Common/Button'
import toast from 'react-hot-toast'

interface UploadFile {
  id: string
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error'
  error?: string
}

const DocumentUpload: React.FC = () => {
  const { currentProfile } = useAppStore()
  const { addDocument, setUploadProgress, removeUploadProgress } = useDocumentStore()
  
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([])
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const supportedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'text/markdown']
  const supportedExtensions = ['.pdf', '.docx', '.txt', '.md']

  const validateFile = (file: File): string | null => {
    // Check file type
    if (!supportedTypes.includes(file.type) && !supportedExtensions.some(ext => file.name.toLowerCase().endsWith(ext))) {
      return 'Unsupported file type. Please upload PDF, DOCX, TXT, or MD files.'
    }

    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024
    if (file.size > maxSize) {
      return 'File size exceeds 10MB limit.'
    }

    return null
  }

  const generateFileId = () => Math.random().toString(36).substr(2, 9)

  const addFiles = useCallback((files: FileList | File[]) => {
    if (!currentProfile) {
      toast.error('Please select a profile first')
      return
    }

    const fileArray = Array.from(files)
    const newUploadFiles: UploadFile[] = []

    fileArray.forEach(file => {
      const error = validateFile(file)
      if (error) {
        toast.error(`${file.name}: ${error}`)
        return
      }

      newUploadFiles.push({
        id: generateFileId(),
        file,
        progress: 0,
        status: 'pending'
      })
    })

    setUploadFiles(prev => [...prev, ...newUploadFiles])
  }, [currentProfile])

  const uploadFile = async (uploadFile: UploadFile) => {
    if (!currentProfile) return

    try {
      setUploadFiles(prev => prev.map(f => 
        f.id === uploadFile.id ? { ...f, status: 'uploading' } : f
      ))

      const document = await apiService.uploadDocument(
        uploadFile.file,
        currentProfile.id,
        (progress) => {
          setUploadFiles(prev => prev.map(f => 
            f.id === uploadFile.id ? { ...f, progress } : f
          ))
          setUploadProgress(uploadFile.id, progress)
        }
      )

      setUploadFiles(prev => prev.map(f => 
        f.id === uploadFile.id ? { ...f, status: 'processing', progress: 100 } : f
      ))

      // Start processing
      await apiService.processDocument(document.id, currentProfile.id)
      
      setUploadFiles(prev => prev.map(f => 
        f.id === uploadFile.id ? { ...f, status: 'completed' } : f
      ))

      addDocument(document)
      removeUploadProgress(uploadFile.id)
      
      // Remove from upload list after 3 seconds
      setTimeout(() => {
        setUploadFiles(prev => prev.filter(f => f.id !== uploadFile.id))
      }, 3000)

    } catch (error: any) {
      setUploadFiles(prev => prev.map(f => 
        f.id === uploadFile.id ? { 
          ...f, 
          status: 'error', 
          error: error.message || 'Upload failed' 
        } : f
      ))
      removeUploadProgress(uploadFile.id)
    }
  }

  const removeFile = (fileId: string) => {
    setUploadFiles(prev => prev.filter(f => f.id !== fileId))
    removeUploadProgress(fileId)
  }

  const uploadAllFiles = () => {
    uploadFiles
      .filter(f => f.status === 'pending')
      .forEach(uploadFile)
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    if (e.dataTransfer.files) {
      addFiles(e.dataTransfer.files)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      addFiles(e.target.files)
    }
  }

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'pending':
        return <File className="w-4 h-4 text-gray-400" />
      case 'uploading':
      case 'processing':
        return <Loader className="w-4 h-4 text-blue-500 animate-spin" />
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return <File className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusText = (status: UploadFile['status']) => {
    switch (status) {
      case 'pending':
        return 'Ready to upload'
      case 'uploading':
        return 'Uploading...'
      case 'processing':
        return 'Processing...'
      case 'completed':
        return 'Completed'
      case 'error':
        return 'Failed'
      default:
        return 'Unknown'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-medium text-gray-900">
            Upload Documents
          </h2>
          {currentProfile && (
            <span className="text-sm text-gray-500">
              Profile: {currentProfile.name}
            </span>
          )}
        </div>

        {!currentProfile && (
          <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
            <p className="text-yellow-800 text-sm">
              Please select a profile before uploading documents.
            </p>
          </div>
        )}

        {/* Drag and Drop Area */}
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            isDragOver
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          } ${!currentProfile ? 'opacity-50 pointer-events-none' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Drop files here or click to browse
          </h3>
          <p className="text-gray-600 mb-4">
            Supports PDF, DOCX, TXT, and MD files up to 10MB
          </p>
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={!currentProfile}
            className="mx-auto"
          >
            Select Files
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.txt,.md"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>

        {/* Upload Queue */}
        {uploadFiles.length > 0 && (
          <div className="mt-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-md font-medium text-gray-900">
                Upload Queue ({uploadFiles.length})
              </h3>
              <div className="flex gap-2">
                <Button
                  onClick={uploadAllFiles}
                  disabled={!uploadFiles.some(f => f.status === 'pending')}
                  size="sm"
                >
                  Upload All
                </Button>
                <Button
                  onClick={() => setUploadFiles([])}
                  variant="secondary"
                  size="sm"
                >
                  Clear Queue
                </Button>
              </div>
            </div>

            <div className="space-y-3">
              {uploadFiles.map((uploadFile) => (
                <div
                  key={uploadFile.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                >
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    {getStatusIcon(uploadFile.status)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {uploadFile.file.name}
                      </p>
                      <div className="flex items-center space-x-2 mt-1">
                        <p className="text-xs text-gray-500">
                          {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                        <span className="text-xs text-gray-400">•</span>
                        <p className={`text-xs ${
                          uploadFile.status === 'error' ? 'text-red-600' :
                          uploadFile.status === 'completed' ? 'text-green-600' :
                          'text-gray-500'
                        }`}>
                          {getStatusText(uploadFile.status)}
                        </p>
                        {uploadFile.error && (
                          <span className="text-xs text-red-600">
                            - {uploadFile.error}
                          </span>
                        )}
                      </div>
                      {(uploadFile.status === 'uploading' || uploadFile.status === 'processing') && (
                        <div className="mt-2">
                          <div className="bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${uploadFile.progress}%` }}
                            />
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-2 ml-4">
                    {uploadFile.status === 'pending' && (
                      <Button
                        onClick={() => uploadFile(uploadFile)}
                        size="sm"
                        variant="primary"
                      >
                        Upload
                      </Button>
                    )}
                    {uploadFile.status === 'error' && (
                      <Button
                        onClick={() => uploadFile(uploadFile)}
                        size="sm"
                        variant="primary"
                      >
                        Retry
                      </Button>
                    )}
                    <button
                      onClick={() => removeFile(uploadFile.id)}
                      className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                      disabled={uploadFile.status === 'uploading' || uploadFile.status === 'processing'}
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Upload Instructions */}
        <div className="mt-6 text-sm text-gray-600">
          <h4 className="font-medium mb-2">Supported File Types:</h4>
          <ul className="list-disc list-inside space-y-1">
            <li><strong>PDF:</strong> Text-based PDF documents (not scanned images)</li>
            <li><strong>DOCX:</strong> Microsoft Word documents</li>
            <li><strong>TXT:</strong> Plain text files</li>
            <li><strong>MD:</strong> Markdown files</li>
          </ul>
          <p className="mt-3">
            <strong>Maximum file size:</strong> 10MB per file
          </p>
        </div>
      </div>
    </div>
  )
}

export default DocumentUpload
