"""
File processing utilities for CLI commands.
"""

import asyncio
import aiofiles
import uuid
from pathlib import Path
from typing import Optional, Callable, Dict, Any
import mimetypes
import requests
from urllib.parse import urlparse

from core.database import AsyncSessionLocal
from core.db_utils import DocumentRepository
from core.chunking import get_document_processor
from core.embeddings import get_embedding_generator
from core.ai_providers import get_provider_manager

class FileProcessor:
    """Handles file processing operations for CLI."""
    
    def __init__(self):
        self.document_processor = get_document_processor()
        self.embedding_generator = get_embedding_generator()
        self.provider_manager = get_provider_manager()
    
    async def upload_document(
        self,
        file_path: Path,
        profile_id: int,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Any:
        """Upload a document to the database."""
        async with AsyncSessionLocal() as db:
            repo = DocumentRepository(db)
            
            # Read file
            if progress_callback:
                progress_callback(10)
            
            async with aiofiles.open(file_path, 'rb') as f:
                file_content = await f.read()
            
            if progress_callback:
                progress_callback(30)
            
            # Get file info
            file_size = len(file_content)
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Create document record
            document_data = {
                'filename': file_path.name,
                'original_filename': file_path.name,
                'file_size': file_size,
                'mime_type': mime_type,
                'profile_id': profile_id,
                'processed': False,
                'metadata': {
                    'source': 'cli_upload',
                    'file_path': str(file_path),
                    'file_extension': file_path.suffix.lower()
                }
            }
            
            if progress_callback:
                progress_callback(60)
            
            document = await repo.create(**document_data)
            
            if progress_callback:
                progress_callback(100)
            
            return document
    
    async def process_document(
        self,
        document_id: str,
        profile_id: int,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> None:
        """Process a document into chunks and embeddings."""
        async with AsyncSessionLocal() as db:
            repo = DocumentRepository(db)
            document = await repo.get_by_id(document_id)
            
            if not document:
                raise ValueError(f"Document {document_id} not found")
            
            if progress_callback:
                progress_callback(10)
            
            # Get document content (this would need to be implemented based on your storage)
            # For now, we'll simulate the processing
            
            # Process document into chunks
            if progress_callback:
                progress_callback(30)
            
            # This would call the actual document processing logic
            # For now, we'll simulate it
            await asyncio.sleep(0.1)  # Simulate processing time
            
            if progress_callback:
                progress_callback(60)
            
            # Generate embeddings for chunks
            # This would call the actual embedding generation
            await asyncio.sleep(0.1)  # Simulate embedding generation
            
            if progress_callback:
                progress_callback(90)
            
            # Mark document as processed
            await repo.update(document_id, processed=True)
            
            if progress_callback:
                progress_callback(100)
    
    async def ingest_url(
        self,
        url: str,
        profile_id: int,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Any:
        """Ingest content from a URL."""
        async with AsyncSessionLocal() as db:
            repo = DocumentRepository(db)
            
            if progress_callback:
                progress_callback(10)
            
            # Download content from URL
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                content = response.text
            except Exception as e:
                raise ValueError(f"Failed to download URL: {str(e)}")
            
            if progress_callback:
                progress_callback(30)
            
            # Parse URL for metadata
            parsed_url = urlparse(url)
            filename = Path(parsed_url.path).name or "web_content.txt"
            
            # Create document record
            document_data = {
                'filename': filename,
                'original_filename': filename,
                'file_size': len(content.encode('utf-8')),
                'mime_type': 'text/html' if 'html' in response.headers.get('content-type', '') else 'text/plain',
                'profile_id': profile_id,
                'processed': False,
                'metadata': {
                    'source': 'url',
                    'url': url,
                    'domain': parsed_url.netloc,
                    'content_type': response.headers.get('content-type', '')
                }
            }
            
            if progress_callback:
                progress_callback(60)
            
            document = await repo.create(**document_data)
            
            if progress_callback:
                progress_callback(80)
            
            # Process the content
            await self.process_document(
                document_id=document.id,
                profile_id=profile_id,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
            
            if progress_callback:
                progress_callback(100)
            
            return document
    
    async def batch_process_files(
        self,
        file_paths: list[Path],
        profile_id: int,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Dict[str, Any]:
        """Process multiple files in batch."""
        results = {
            'successful': [],
            'failed': [],
            'total': len(file_paths)
        }
        
        for i, file_path in enumerate(file_paths):
            try:
                # Upload document
                document = await self.upload_document(file_path, profile_id)
                
                # Process document
                await self.process_document(
                    document_id=document.id,
                    profile_id=profile_id,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
                
                results['successful'].append({
                    'file': str(file_path),
                    'document_id': document.id
                })
                
            except Exception as e:
                results['failed'].append({
                    'file': str(file_path),
                    'error': str(e)
                })
            
            # Update progress
            if progress_callback:
                progress = int((i + 1) / len(file_paths) * 100)
                progress_callback(progress)
        
        return results
    
    def get_supported_extensions(self) -> set[str]:
        """Get list of supported file extensions."""
        return {'.pdf', '.doc', '.docx', '.txt', '.md', '.rtf'}
    
    def is_supported_file(self, file_path: Path) -> bool:
        """Check if file is supported."""
        return file_path.suffix.lower() in self.get_supported_extensions()
    
    async def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get information about a file."""
        stat = file_path.stat()
        
        return {
            'name': file_path.name,
            'size': stat.st_size,
            'extension': file_path.suffix.lower(),
            'modified': stat.st_mtime,
            'supported': self.is_supported_file(file_path)
        }
