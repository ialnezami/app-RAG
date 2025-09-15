"""
Profile management endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from core.database import get_db
from core.db_utils import ProfileRepository
from core.ai_providers import get_provider_manager
from config.settings import get_settings

router = APIRouter()


# Pydantic models for request/response
class ProfileCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Profile name")
    description: Optional[str] = Field(None, max_length=1000, description="Profile description")
    prompt: str = Field(..., min_length=1, description="AI prompt template")
    provider: str = Field(..., description="AI provider name")
    model: str = Field(..., description="AI model name")
    settings: dict = Field(default_factory=dict, description="Profile settings")


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    prompt: Optional[str] = Field(None, min_length=1)
    provider: Optional[str] = None
    model: Optional[str] = None
    settings: Optional[dict] = None


class ProfileResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    prompt: str
    provider: str
    model: str
    settings: dict
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ProfileListResponse(BaseModel):
    profiles: List[ProfileResponse]
    total: int
    page: int
    limit: int


@router.get("/profiles", response_model=ProfileListResponse)
async def list_profiles(
    page: int = 1,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List all profiles with pagination."""
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 50
    
    profile_repo = ProfileRepository(db)
    profiles = await profile_repo.get_all()
    
    # Simple pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_profiles = profiles[start_idx:end_idx]
    
    return ProfileListResponse(
        profiles=[
            ProfileResponse(
                id=p.id,
                name=p.name,
                description=p.description,
                prompt=p.prompt,
                provider=p.provider,
                model=p.model,
                settings=p.settings,
                created_at=p.created_at.isoformat(),
                updated_at=p.updated_at.isoformat()
            )
            for p in paginated_profiles
        ],
        total=len(profiles),
        page=page,
        limit=limit
    )


@router.get("/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific profile by ID."""
    profile_repo = ProfileRepository(db)
    profile = await profile_repo.get_by_id(profile_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    return ProfileResponse(
        id=profile.id,
        name=profile.name,
        description=profile.description,
        prompt=profile.prompt,
        provider=profile.provider,
        model=profile.model,
        settings=profile.settings,
        created_at=profile.created_at.isoformat(),
        updated_at=profile.updated_at.isoformat()
    )


@router.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new profile."""
    # Validate provider and model
    provider_manager = get_provider_manager()
    if profile_data.provider not in provider_manager.get_available_providers():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{profile_data.provider}' is not available"
        )
    
    available_models = provider_manager.get_available_models(profile_data.provider)
    if profile_data.model not in available_models:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{profile_data.model}' is not available for provider '{profile_data.provider}'"
        )
    
    profile_repo = ProfileRepository(db)
    
    try:
        profile = await profile_repo.create(
            name=profile_data.name,
            description=profile_data.description,
            prompt=profile_data.prompt,
            provider=profile_data.provider,
            model=profile_data.model,
            settings=profile_data.settings
        )
        
        return ProfileResponse(
            id=profile.id,
            name=profile.name,
            description=profile.description,
            prompt=profile.prompt,
            provider=profile.provider,
            model=profile.model,
            settings=profile.settings,
            created_at=profile.created_at.isoformat(),
            updated_at=profile.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create profile: {str(e)}"
        )


@router.put("/profiles/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile_data: ProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing profile."""
    profile_repo = ProfileRepository(db)
    
    # Check if profile exists
    existing_profile = await profile_repo.get_by_id(profile_id)
    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    # Validate provider and model if provided
    provider_manager = get_provider_manager()
    if profile_data.provider:
        if profile_data.provider not in provider_manager.get_available_providers():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{profile_data.provider}' is not available"
            )
        
        if profile_data.model:
            available_models = provider_manager.get_available_models(profile_data.provider)
            if profile_data.model not in available_models:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Model '{profile_data.model}' is not available for provider '{profile_data.provider}'"
                )
    
    # Prepare update data
    update_data = {}
    if profile_data.name is not None:
        update_data["name"] = profile_data.name
    if profile_data.description is not None:
        update_data["description"] = profile_data.description
    if profile_data.prompt is not None:
        update_data["prompt"] = profile_data.prompt
    if profile_data.provider is not None:
        update_data["provider"] = profile_data.provider
    if profile_data.model is not None:
        update_data["model"] = profile_data.model
    if profile_data.settings is not None:
        update_data["settings"] = profile_data.settings
    
    try:
        updated_profile = await profile_repo.update(profile_id, **update_data)
        
        return ProfileResponse(
            id=updated_profile.id,
            name=updated_profile.name,
            description=updated_profile.description,
            prompt=updated_profile.prompt,
            provider=updated_profile.provider,
            model=updated_profile.model,
            settings=updated_profile.settings,
            created_at=updated_profile.created_at.isoformat(),
            updated_at=updated_profile.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a profile."""
    profile_repo = ProfileRepository(db)
    
    # Check if profile exists
    existing_profile = await profile_repo.get_by_id(profile_id)
    if not existing_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    try:
        success = await profile_repo.delete(profile_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete profile"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete profile: {str(e)}"
        )


@router.get("/profiles/{profile_id}/stats")
async def get_profile_stats(
    profile_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for a profile."""
    from core.retrieval import get_vector_retriever
    
    profile_repo = ProfileRepository(db)
    profile = await profile_repo.get_by_id(profile_id)
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile with ID {profile_id} not found"
        )
    
    # Get vector statistics
    vector_retriever = get_vector_retriever()
    stats = await vector_retriever.get_profile_statistics(db, profile_id)
    
    return {
        "profile_id": profile_id,
        "profile_name": profile.name,
        "statistics": stats
    }


@router.get("/config/providers")
async def get_available_providers():
    """Get available AI providers and their models."""
    provider_manager = get_provider_manager()
    
    providers = {}
    for provider_name in provider_manager.get_available_providers():
        models = provider_manager.get_available_models(provider_name)
        provider_instance = provider_manager.get_provider(provider_name)
        
        providers[provider_name] = {
            "name": provider_instance.config.get("name", provider_name),
            "base_url": provider_instance.config.get("base_url", ""),
            "models": {}
        }
        
        for model in models:
            model_config = provider_instance.get_model_config(model)
            providers[provider_name]["models"][model] = {
                "name": model_config.get("name", model),
                "max_tokens": model_config.get("max_tokens"),
                "temperature": model_config.get("temperature"),
                "cost_per_1k_tokens": model_config.get("cost_per_1k_tokens"),
                "dimensions": model_config.get("dimensions")  # For embedding models
            }
    
    return {
        "providers": providers,
        "total_providers": len(providers),
        "total_models": sum(len(models["models"]) for models in providers.values())
    }


@router.get("/config/models")
async def get_available_models(provider: Optional[str] = None):
    """Get available models, optionally filtered by provider."""
    provider_manager = get_provider_manager()
    
    if provider:
        if provider not in provider_manager.get_available_providers():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Provider '{provider}' is not available"
            )
        
        models = provider_manager.get_available_models(provider)
        provider_instance = provider_manager.get_provider(provider)
        
        return {
            "provider": provider,
            "models": {
                model: provider_instance.get_model_config(model)
                for model in models
            },
            "total_models": len(models)
        }
    else:
        # Return all models from all providers
        all_models = {}
        for provider_name in provider_manager.get_available_providers():
            models = provider_manager.get_available_models(provider_name)
            provider_instance = provider_manager.get_provider(provider_name)
            
            all_models[provider_name] = {
                model: provider_instance.get_model_config(model)
                for model in models
            }
        
        return {
            "all_models": all_models,
            "total_providers": len(all_models),
            "total_models": sum(len(models) for models in all_models.values())
        }
