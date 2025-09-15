"""
AI provider abstractions and implementations.
"""
import os
import json
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
import httpx
import openai
import google.generativeai as genai
import anthropic
from config.settings import get_settings


@dataclass
class AIResponse:
    """AI response data structure."""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None
    error: Optional[str] = None


@dataclass
class EmbeddingResponse:
    """Embedding response data structure."""
    embedding: List[float]
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None


class BaseAIProvider(ABC):
    """Base class for AI providers."""
    
    def __init__(self, provider_name: str, config: Dict[str, Any]):
        self.provider_name = provider_name
        self.config = config
        self.settings = get_settings()
    
    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AIResponse:
        """Generate a response from the AI model."""
        pass
    
    @abstractmethod
    async def generate_embedding(
        self,
        text: str,
        model: str
    ) -> EmbeddingResponse:
        """Generate embeddings for text."""
        pass
    
    @abstractmethod
    async def stream_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response from the AI model."""
        pass
    
    def get_model_config(self, model: str) -> Dict[str, Any]:
        """Get configuration for a specific model."""
        return self.config.get("models", {}).get(model, {})


class OpenAIProvider(BaseAIProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("openai", config)
        self.api_key = self.settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
        
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
    
    async def generate_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AIResponse:
        """Generate response using OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return AIResponse(
                content=response.choices[0].message.content,
                model=model,
                provider=self.provider_name,
                usage=response.usage.dict() if response.usage else None,
                finish_reason=response.choices[0].finish_reason
            )
        except Exception as e:
            return AIResponse(
                content="",
                model=model,
                provider=self.provider_name,
                error=str(e)
            )
    
    async def generate_embedding(
        self,
        text: str,
        model: str
    ) -> EmbeddingResponse:
        """Generate embeddings using OpenAI API."""
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=text
            )
            
            return EmbeddingResponse(
                embedding=response.data[0].embedding,
                model=model,
                provider=self.provider_name,
                usage=response.usage.dict() if response.usage else None
            )
        except Exception as e:
            return EmbeddingResponse(
                embedding=[],
                model=model,
                provider=self.provider_name,
                error=str(e)
            )
    
    async def stream_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response using OpenAI API."""
        try:
            stream = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"


class AnthropicProvider(BaseAIProvider):
    """Anthropic provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("anthropic", config)
        self.api_key = self.settings.anthropic_api_key
        if not self.api_key:
            raise ValueError("Anthropic API key not found")
        
        self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
    
    async def generate_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AIResponse:
        """Generate response using Anthropic API."""
        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            
            return AIResponse(
                content=response.content[0].text,
                model=model,
                provider=self.provider_name,
                usage=response.usage.dict() if response.usage else None,
                finish_reason=response.stop_reason
            )
        except Exception as e:
            return AIResponse(
                content="",
                model=model,
                provider=self.provider_name,
                error=str(e)
            )
    
    async def generate_embedding(
        self,
        text: str,
        model: str
    ) -> EmbeddingResponse:
        """Anthropic doesn't provide embeddings directly."""
        return EmbeddingResponse(
            embedding=[],
            model=model,
            provider=self.provider_name,
            error="Anthropic doesn't provide embedding models"
        )
    
    async def stream_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response using Anthropic API."""
        try:
            async with self.client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            yield f"Error: {str(e)}"


class GoogleProvider(BaseAIProvider):
    """Google Gemini provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("google", config)
        self.api_key = self.settings.google_api_key
        if not self.api_key:
            raise ValueError("Google API key not found")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AIResponse:
        """Generate response using Google Gemini API."""
        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )
            
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            return AIResponse(
                content=response.text,
                model=model,
                provider=self.provider_name,
                usage=response.usage_metadata.dict() if response.usage_metadata else None
            )
        except Exception as e:
            return AIResponse(
                content="",
                model=model,
                provider=self.provider_name,
                error=str(e)
            )
    
    async def generate_embedding(
        self,
        text: str,
        model: str
    ) -> EmbeddingResponse:
        """Generate embeddings using Google API."""
        try:
            result = await genai.embed_content_async(
                model=model,
                content=text,
                task_type="retrieval_document"
            )
            
            return EmbeddingResponse(
                embedding=result['embedding'],
                model=model,
                provider=self.provider_name
            )
        except Exception as e:
            return EmbeddingResponse(
                embedding=[],
                model=model,
                provider=self.provider_name,
                error=str(e)
            )
    
    async def stream_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response using Google Gemini API."""
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                **kwargs
            )
            
            async for chunk in self.model.generate_content_async(
                prompt,
                generation_config=generation_config,
                stream=True
            ):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"Error: {str(e)}"


class CustomProvider(BaseAIProvider):
    """Custom API provider implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("custom", config)
        self.base_url = config.get("base_url", "http://localhost:11434/v1")
        self.api_key = os.getenv("CUSTOM_API_KEY")
    
    async def generate_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AIResponse:
        """Generate response using custom API."""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    **kwargs
                }
                
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                return AIResponse(
                    content=result["choices"][0]["message"]["content"],
                    model=model,
                    provider=self.provider_name,
                    usage=result.get("usage"),
                    finish_reason=result["choices"][0].get("finish_reason")
                )
        except Exception as e:
            return AIResponse(
                content="",
                model=model,
                provider=self.provider_name,
                error=str(e)
            )
    
    async def generate_embedding(
        self,
        text: str,
        model: str
    ) -> EmbeddingResponse:
        """Generate embeddings using custom API."""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                data = {
                    "model": model,
                    "input": text
                }
                
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                return EmbeddingResponse(
                    embedding=result["data"][0]["embedding"],
                    model=model,
                    provider=self.provider_name,
                    usage=result.get("usage")
                )
        except Exception as e:
            return EmbeddingResponse(
                embedding=[],
                model=model,
                provider=self.provider_name,
                error=str(e)
            )
    
    async def stream_response(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response using custom API."""
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                    **kwargs
                }
                
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and chunk["choices"]:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            yield f"Error: {str(e)}"


class AIProviderManager:
    """Manager for AI providers."""
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.config = self._load_config()
        self._initialize_providers()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load AI provider configuration."""
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.json")
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"ai_providers": {}}
    
    def _initialize_providers(self):
        """Initialize available providers."""
        provider_classes = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "google": GoogleProvider,
            "custom": CustomProvider
        }
        
        for provider_name, provider_config in self.config.get("ai_providers", {}).items():
            try:
                if provider_name in provider_classes:
                    provider_class = provider_classes[provider_name]
                    self.providers[provider_name] = provider_class(provider_config)
            except Exception as e:
                print(f"Failed to initialize {provider_name} provider: {e}")
    
    def get_provider(self, provider_name: str) -> Optional[BaseAIProvider]:
        """Get a provider by name."""
        return self.providers.get(provider_name)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self.providers.keys())
    
    def get_available_models(self, provider_name: str) -> List[str]:
        """Get available models for a provider."""
        provider = self.get_provider(provider_name)
        if provider:
            return list(provider.config.get("models", {}).keys())
        return []
    
    async def generate_response(
        self,
        provider_name: str,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AIResponse:
        """Generate response using specified provider."""
        provider = self.get_provider(provider_name)
        if not provider:
            return AIResponse(
                content="",
                model=model,
                provider=provider_name,
                error=f"Provider {provider_name} not available"
            )
        
        return await provider.generate_response(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    async def generate_embedding(
        self,
        provider_name: str,
        model: str,
        text: str
    ) -> EmbeddingResponse:
        """Generate embedding using specified provider."""
        provider = self.get_provider(provider_name)
        if not provider:
            return EmbeddingResponse(
                embedding=[],
                model=model,
                provider=provider_name,
                error=f"Provider {provider_name} not available"
            )
        
        return await provider.generate_embedding(text=text, model=model)
    
    async def stream_response(
        self,
        provider_name: str,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream response using specified provider."""
        provider = self.get_provider(provider_name)
        if not provider:
            yield f"Error: Provider {provider_name} not available"
            return
        
        async for chunk in provider.stream_response(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            yield chunk


# Global provider manager instance
_provider_manager: Optional[AIProviderManager] = None


def get_provider_manager() -> AIProviderManager:
    """Get the global provider manager instance."""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = AIProviderManager()
    return _provider_manager
