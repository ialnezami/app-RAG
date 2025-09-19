"""
Multi-tenant support for the RAG application.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException, status, Depends, Request
import logging

from .database import get_db
from .models import Profile, Document, DocumentChunk, ChatSession, ChatMessage

logger = logging.getLogger(__name__)

class TenantContext:
    """Tenant context for multi-tenant operations."""
    
    def __init__(self, tenant_id: Optional[str] = None, tenant_name: Optional[str] = None):
        self.tenant_id = tenant_id
        self.tenant_name = tenant_name
        self.is_multi_tenant = tenant_id is not None
    
    def __str__(self):
        if self.is_multi_tenant:
            return f"Tenant({self.tenant_id}:{self.tenant_name})"
        return "SingleTenant"

class TenantManager:
    """Manages tenant isolation and operations."""
    
    def __init__(self):
        self.tenants: Dict[str, Dict[str, Any]] = {}
        self.default_tenant = "default"
    
    def get_tenant_from_request(self, request: Request) -> TenantContext:
        """Extract tenant information from request."""
        # Check for tenant in headers
        tenant_id = request.headers.get("X-Tenant-ID")
        tenant_name = request.headers.get("X-Tenant-Name")
        
        # Check for tenant in subdomain
        if not tenant_id:
            host = request.headers.get("host", "")
            if "." in host:
                subdomain = host.split(".")[0]
                if subdomain and subdomain != "www" and subdomain != "api":
                    tenant_id = subdomain
        
        # Check for tenant in query parameters
        if not tenant_id:
            tenant_id = request.query_params.get("tenant_id")
        
        # Default to single tenant mode
        if not tenant_id:
            return TenantContext()
        
        return TenantContext(tenant_id=tenant_id, tenant_name=tenant_name)
    
    def create_tenant(self, tenant_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new tenant with configuration."""
        if tenant_id in self.tenants:
            raise ValueError(f"Tenant {tenant_id} already exists")
        
        tenant_config = {
            "id": tenant_id,
            "name": config.get("name", tenant_id),
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
            "limits": {
                "max_profiles": config.get("max_profiles", 10),
                "max_documents": config.get("max_documents", 1000),
                "max_storage_mb": config.get("max_storage_mb", 1000),
                "max_api_calls_per_hour": config.get("max_api_calls_per_hour", 1000)
            },
            "features": {
                "advanced_analytics": config.get("advanced_analytics", False),
                "custom_models": config.get("custom_models", False),
                "api_access": config.get("api_access", True),
                "webhook_support": config.get("webhook_support", False)
            },
            "settings": config.get("settings", {})
        }
        
        self.tenants[tenant_id] = tenant_config
        logger.info(f"Created tenant: {tenant_id}")
        
        return tenant_config
    
    def get_tenant(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant configuration."""
        return self.tenants.get(tenant_id)
    
    def list_tenants(self) -> List[Dict[str, Any]]:
        """List all tenants."""
        return list(self.tenants.values())
    
    def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update tenant configuration."""
        if tenant_id not in self.tenants:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        tenant = self.tenants[tenant_id]
        
        # Update basic info
        if "name" in updates:
            tenant["name"] = updates["name"]
        
        if "status" in updates:
            tenant["status"] = updates["status"]
        
        # Update limits
        if "limits" in updates:
            tenant["limits"].update(updates["limits"])
        
        # Update features
        if "features" in updates:
            tenant["features"].update(updates["features"])
        
        # Update settings
        if "settings" in updates:
            tenant["settings"].update(updates["settings"])
        
        tenant["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Updated tenant: {tenant_id}")
        return tenant
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant."""
        if tenant_id not in self.tenants:
            return False
        
        del self.tenants[tenant_id]
        logger.info(f"Deleted tenant: {tenant_id}")
        return True
    
    def check_tenant_limits(self, tenant_context: TenantContext, resource_type: str, current_count: int) -> bool:
        """Check if tenant is within limits for a resource."""
        if not tenant_context.is_multi_tenant:
            return True  # No limits in single tenant mode
        
        tenant = self.get_tenant(tenant_context.tenant_id)
        if not tenant:
            return False
        
        limits = tenant.get("limits", {})
        limit_key = f"max_{resource_type}"
        
        if limit_key in limits:
            return current_count < limits[limit_key]
        
        return True
    
    def has_feature(self, tenant_context: TenantContext, feature_name: str) -> bool:
        """Check if tenant has access to a feature."""
        if not tenant_context.is_multi_tenant:
            return True  # All features available in single tenant mode
        
        tenant = self.get_tenant(tenant_context.tenant_id)
        if not tenant:
            return False
        
        features = tenant.get("features", {})
        return features.get(feature_name, False)

class TenantAwareRepository:
    """Base class for tenant-aware database operations."""
    
    def __init__(self, session: AsyncSession, tenant_context: TenantContext):
        self.session = session
        self.tenant_context = tenant_context
    
    def add_tenant_filter(self, query, model_class):
        """Add tenant filter to query if in multi-tenant mode."""
        if self.tenant_context.is_multi_tenant and hasattr(model_class, 'tenant_id'):
            return query.where(model_class.tenant_id == self.tenant_context.tenant_id)
        return query
    
    def set_tenant_id(self, obj):
        """Set tenant ID on object if in multi-tenant mode."""
        if self.tenant_context.is_multi_tenant and hasattr(obj, 'tenant_id'):
            obj.tenant_id = self.tenant_context.tenant_id
        return obj

class TenantAwareProfileRepository(TenantAwareRepository):
    """Tenant-aware profile operations."""
    
    async def get_profiles(self) -> List[Profile]:
        """Get profiles for current tenant."""
        query = select(Profile)
        query = self.add_tenant_filter(query, Profile)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create_profile(self, profile_data: Dict[str, Any]) -> Profile:
        """Create profile for current tenant."""
        profile = Profile(**profile_data)
        profile = self.set_tenant_id(profile)
        
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        
        return profile

class TenantAwareDocumentRepository(TenantAwareRepository):
    """Tenant-aware document operations."""
    
    async def get_documents(self, profile_id: int) -> List[Document]:
        """Get documents for current tenant and profile."""
        query = select(Document).where(Document.profile_id == profile_id)
        query = self.add_tenant_filter(query, Document)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create_document(self, document_data: Dict[str, Any]) -> Document:
        """Create document for current tenant."""
        document = Document(**document_data)
        document = self.set_tenant_id(document)
        
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        
        return document

# Global tenant manager instance
tenant_manager = TenantManager()

def get_tenant_context(request: Request) -> TenantContext:
    """Dependency to get tenant context from request."""
    return tenant_manager.get_tenant_from_request(request)

def get_tenant_aware_profile_repo(
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_db)
) -> TenantAwareProfileRepository:
    """Get tenant-aware profile repository."""
    return TenantAwareProfileRepository(session, tenant_context)

def get_tenant_aware_document_repo(
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_db)
) -> TenantAwareDocumentRepository:
    """Get tenant-aware document repository."""
    return TenantAwareDocumentRepository(session, tenant_context)

def require_tenant_feature(feature_name: str):
    """Decorator to require a specific tenant feature."""
    def decorator(func):
        async def wrapper(*args, tenant_context: TenantContext = Depends(get_tenant_context), **kwargs):
            if not tenant_manager.has_feature(tenant_context, feature_name):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Feature '{feature_name}' not available for this tenant"
                )
            return await func(*args, tenant_context=tenant_context, **kwargs)
        return wrapper
    return decorator
