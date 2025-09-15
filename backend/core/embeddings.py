"""
Embedding generation and management.
"""
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

from .ai_providers import get_provider_manager, EmbeddingResponse
from config.settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingResult:
    """Result of embedding generation."""
    embeddings: List[List[float]]
    model: str
    provider: str
    total_tokens: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class EmbeddingGenerator:
    """Handles embedding generation for text chunks."""
    
    def __init__(self):
        self.settings = get_settings()
        self.provider_manager = get_provider_manager()
        self.local_model = None
        self._initialize_local_model()
    
    def _initialize_local_model(self):
        """Initialize local sentence transformer model as fallback."""
        try:
            # Use a lightweight model for local embeddings
            self.local_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Local embedding model initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize local embedding model: {e}")
            self.local_model = None
    
    async def generate_embeddings(
        self,
        texts: List[str],
        provider: str = None,
        model: str = None,
        batch_size: int = None
    ) -> EmbeddingResult:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of texts to embed
            provider: AI provider to use (default from config)
            model: Model to use (default from config)
            batch_size: Batch size for processing
            
        Returns:
            EmbeddingResult with embeddings and metadata
        """
        if not texts:
            return EmbeddingResult(
                embeddings=[],
                model=model or self.settings.default_embedding_model,
                provider=provider or self.settings.default_embedding_provider
            )
        
        # Use defaults if not specified
        provider = provider or self.settings.default_embedding_provider
        model = model or self.settings.default_embedding_model
        batch_size = batch_size or 100
        
        logger.info(f"Generating embeddings for {len(texts)} texts using {provider}/{model}")
        
        # Try AI provider first
        embeddings = []
        errors = []
        total_tokens = 0
        
        try:
            embeddings, total_tokens, errors = await self._generate_with_provider(
                texts, provider, model, batch_size
            )
        except Exception as e:
            logger.error(f"Provider embedding failed: {e}")
            errors.append(f"Provider embedding failed: {str(e)}")
        
        # Fallback to local model if provider failed or no embeddings
        if not embeddings and self.local_model:
            logger.info("Falling back to local embedding model")
            try:
                embeddings = await self._generate_local_embeddings(texts, batch_size)
            except Exception as e:
                logger.error(f"Local embedding failed: {e}")
                errors.append(f"Local embedding failed: {str(e)}")
        
        return EmbeddingResult(
            embeddings=embeddings,
            model=model,
            provider=provider,
            total_tokens=total_tokens,
            errors=errors
        )
    
    async def _generate_with_provider(
        self,
        texts: List[str],
        provider: str,
        model: str,
        batch_size: int
    ) -> Tuple[List[List[float]], int, List[str]]:
        """Generate embeddings using AI provider."""
        embeddings = []
        total_tokens = 0
        errors = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.debug(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
            
            # Generate embeddings for batch
            batch_embeddings = await self._generate_batch_embeddings(
                batch, provider, model
            )
            
            # Collect results
            for j, (text, embedding_result) in enumerate(zip(batch, batch_embeddings)):
                if embedding_result.error:
                    errors.append(f"Text {i + j}: {embedding_result.error}")
                    # Use zero vector as fallback
                    embeddings.append([0.0] * self.settings.embedding_dimensions)
                else:
                    embeddings.append(embedding_result.embedding)
                    if embedding_result.usage:
                        total_tokens += embedding_result.usage.get('total_tokens', 0)
        
        return embeddings, total_tokens, errors
    
    async def _generate_batch_embeddings(
        self,
        texts: List[str],
        provider: str,
        model: str
    ) -> List[EmbeddingResponse]:
        """Generate embeddings for a batch of texts."""
        tasks = []
        for text in texts:
            task = self.provider_manager.generate_embedding(
                provider_name=provider,
                model=model,
                text=text
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        embedding_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                embedding_results.append(EmbeddingResponse(
                    embedding=[],
                    model=model,
                    provider=provider,
                    error=str(result)
                ))
            else:
                embedding_results.append(result)
        
        return embedding_results
    
    async def _generate_local_embeddings(
        self,
        texts: List[str],
        batch_size: int
    ) -> List[List[float]]:
        """Generate embeddings using local sentence transformer model."""
        if not self.local_model:
            raise ValueError("Local embedding model not available")
        
        embeddings = []
        
        # Process in batches to avoid memory issues
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            batch_embeddings = await loop.run_in_executor(
                None, self.local_model.encode, batch
            )
            
            # Convert to list of lists
            for embedding in batch_embeddings:
                embeddings.append(embedding.tolist())
        
        return embeddings
    
    async def generate_single_embedding(
        self,
        text: str,
        provider: str = None,
        model: str = None
    ) -> Optional[List[float]]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            provider: AI provider to use
            model: Model to use
            
        Returns:
            Embedding vector or None if failed
        """
        result = await self.generate_embeddings(
            texts=[text],
            provider=provider,
            model=model
        )
        
        if result.embeddings and not result.errors:
            return result.embeddings[0]
        return None
    
    def get_embedding_dimensions(self, provider: str, model: str) -> int:
        """Get embedding dimensions for a specific model."""
        provider_instance = self.provider_manager.get_provider(provider)
        if provider_instance:
            model_config = provider_instance.get_model_config(model)
            return model_config.get("dimensions", self.settings.embedding_dimensions)
        
        return self.settings.embedding_dimensions
    
    async def test_provider(self, provider: str, model: str) -> Dict[str, Any]:
        """
        Test if a provider/model combination works.
        
        Args:
            provider: Provider name
            model: Model name
            
        Returns:
            Test result dictionary
        """
        test_text = "This is a test text for embedding generation."
        
        try:
            start_time = asyncio.get_event_loop().time()
            result = await self.generate_single_embedding(
                text=test_text,
                provider=provider,
                model=model
            )
            end_time = asyncio.get_event_loop().time()
            
            if result:
                return {
                    "success": True,
                    "dimensions": len(result),
                    "response_time": end_time - start_time,
                    "provider": provider,
                    "model": model
                }
            else:
                return {
                    "success": False,
                    "error": "No embedding generated",
                    "provider": provider,
                    "model": model
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "provider": provider,
                "model": model
            }
    
    async def get_available_providers(self) -> Dict[str, List[str]]:
        """Get available embedding providers and models."""
        providers = {}
        
        for provider_name in self.provider_manager.get_available_providers():
            models = self.provider_manager.get_available_models(provider_name)
            embedding_models = []
            
            for model in models:
                model_config = self.provider_manager.get_provider(provider_name).get_model_config(model)
                if "dimensions" in model_config:  # This is an embedding model
                    embedding_models.append(model)
            
            if embedding_models:
                providers[provider_name] = embedding_models
        
        return providers


# Global embedding generator instance
_embedding_generator: Optional[EmbeddingGenerator] = None


def get_embedding_generator() -> EmbeddingGenerator:
    """Get the global embedding generator instance."""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator


# Utility functions
def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    
    # Convert to numpy arrays
    a_np = np.array(a)
    b_np = np.array(b)
    
    # Calculate cosine similarity
    dot_product = np.dot(a_np, b_np)
    norm_a = np.linalg.norm(a_np)
    norm_b = np.linalg.norm(b_np)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)


def euclidean_distance(a: List[float], b: List[float]) -> float:
    """Calculate euclidean distance between two vectors."""
    if not a or not b or len(a) != len(b):
        return float('inf')
    
    # Convert to numpy arrays
    a_np = np.array(a)
    b_np = np.array(b)
    
    # Calculate euclidean distance
    return float(np.linalg.norm(a_np - b_np))


def normalize_vector(vector: List[float]) -> List[float]:
    """Normalize a vector to unit length."""
    if not vector:
        return vector
    
    # Convert to numpy array
    vector_np = np.array(vector)
    
    # Calculate norm
    norm = np.linalg.norm(vector_np)
    
    if norm == 0:
        return vector
    
    # Normalize
    normalized = vector_np / norm
    
    return normalized.tolist()
