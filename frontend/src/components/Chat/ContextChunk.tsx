import React, { useState } from 'react'
import { ChevronDown, ChevronRight, FileText, ExternalLink } from 'lucide-react'
import { ContextChunk as ContextChunkType } from '../../services/types'

interface ContextChunkProps {
  chunk: ContextChunkType
  className?: string
}

const ContextChunk: React.FC<ContextChunkProps> = ({
  chunk,
  className
}) => {
  const [isExpanded, setIsExpanded] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(chunk.content)
    } catch (err) {
      console.error('Failed to copy text:', err)
    }
  }

  return (
    <div className={`context-chunk ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center space-x-1 text-xs font-medium text-gray-600 hover:text-gray-800"
          >
            {isExpanded ? (
              <ChevronDown className="h-3 w-3" />
            ) : (
              <ChevronRight className="h-3 w-3" />
            )}
            <span>Source {chunk.chunk_index + 1}</span>
          </button>
          
          {chunk.document_filename && (
            <span className="context-chunk-source">
              from {chunk.document_filename}
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <span className="context-chunk-similarity">
            {(chunk.similarity * 100).toFixed(1)}% match
          </span>
          
          <button
            onClick={handleCopy}
            className="text-xs text-gray-500 hover:text-gray-700"
            title="Copy content"
          >
            <ExternalLink className="h-3 w-3" />
          </button>
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="context-chunk-content">
          <p className="text-sm leading-relaxed">
            {chunk.content}
          </p>
          
          {/* Metadata */}
          {chunk.metadata && Object.keys(chunk.metadata).length > 0 && (
            <div className="mt-2 pt-2 border-t border-gray-200">
              <details className="text-xs text-gray-500">
                <summary className="cursor-pointer hover:text-gray-700">
                  Metadata
                </summary>
                <div className="mt-1 space-y-1">
                  {Object.entries(chunk.metadata).map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="font-medium">{key}:</span>
                      <span>{String(value)}</span>
                    </div>
                  ))}
                </div>
              </details>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ContextChunk
