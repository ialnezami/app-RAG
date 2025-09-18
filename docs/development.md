# 🛠️ Development Guide

## RAG Application Development Guide

This guide covers development setup, code structure, testing, and contribution guidelines for the RAG application.

## 🚀 Development Environment Setup

### Prerequisites
- **Docker & Docker Compose**: For containerized development
- **Python 3.11+**: For backend development
- **Node.js 18+**: For frontend development
- **Git**: Version control
- **IDE**: VS Code recommended with extensions

### Quick Setup
```bash
# Clone repository
git clone <repository-url>
cd app\ RAG

# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env

# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Initialize database
docker exec -it apprag-backend-1 python cli.py init-db
docker exec -it apprag-backend-1 python cli.py init-profiles
```

### Local Development (Without Docker)

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
# ... other environment variables

# Run backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### Database Setup (Local)
```bash
# Install PostgreSQL with pgvector
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib
sudo -u postgres psql -c "CREATE EXTENSION vector;"

# macOS with Homebrew:
brew install postgresql pgvector
```

## 📁 Project Structure

```
rag-fullstack/
├── backend/                    # FastAPI backend
│   ├── main.py                # Application entry point
│   ├── config/                # Configuration files
│   │   ├── settings.py        # Environment settings
│   │   └── config.json        # AI provider configs
│   ├── api/                   # API routes and WebSocket
│   │   ├── routes/            # REST API endpoints
│   │   └── websocket/         # WebSocket handlers
│   ├── core/                  # Core business logic
│   │   ├── database.py        # Database connection
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── ai_providers.py    # AI provider abstraction
│   │   ├── embeddings.py      # Embedding generation
│   │   ├── chunking.py        # Text chunking
│   │   ├── retrieval.py       # Vector search
│   │   └── db_utils.py        # Database utilities
│   ├── cli/                   # CLI commands
│   └── tests/                 # Test files
├── frontend/                  # React.js frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API services
│   │   ├── store/            # State management
│   │   └── utils/            # Utility functions
│   ├── public/               # Static assets
│   └── package.json          # Dependencies
├── database/                 # Database initialization
├── nginx/                    # Nginx configuration
├── docs/                     # Documentation
├── cli/                      # Standalone CLI tools
└── docker-compose*.yml       # Docker configurations
```

## 🔧 Development Workflow

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

### Code Style and Standards

#### Python (Backend)
```bash
# Install development tools
pip install black isort flake8 mypy

# Format code
black .
isort .

# Lint code
flake8 .
mypy .
```

#### JavaScript/TypeScript (Frontend)
```bash
# Install development tools
npm install -D eslint prettier @typescript-eslint/parser

# Format code
npm run format

# Lint code
npm run lint
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.34.0
    hooks:
      - id: eslint
        files: \.(js|ts|tsx)$
```

## 🧪 Testing

### Backend Testing

#### Setup Test Environment
```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio pytest-mock httpx

# Set test environment variables
export POSTGRES_DB=rag_test
export ENVIRONMENT=testing
```

#### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::test_health_endpoint
```

#### Writing Tests
```python
# tests/test_api.py
import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_create_profile():
    async with AsyncClient(app=app, base_url="http://test") as client:
        profile_data = {
            "name": "Test Profile",
            "description": "Test description",
            "prompt": "Test prompt",
            "provider": "openai",
            "model": "gpt-4o-mini"
        }
        response = await client.post("/api/v1/profiles", json=profile_data)
        assert response.status_code == 201
        assert response.json()["name"] == "Test Profile"
```

### Frontend Testing

#### Setup Test Environment
```bash
cd frontend

# Install test dependencies
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

#### Run Tests
```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test
npm test Button.test.tsx

# Run in watch mode
npm test -- --watch
```

#### Writing Tests
```typescript
// src/components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Button from './Button';

describe('Button', () => {
  it('renders correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### E2E Testing with Playwright
```bash
# Install Playwright
npm install -D @playwright/test

# Install browsers
npx playwright install

# Run E2E tests
npm run test:e2e
```

```typescript
// tests/e2e/chat.spec.ts
import { test, expect } from '@playwright/test';

test('chat flow', async ({ page }) => {
  await page.goto('http://localhost:3000');
  
  // Navigate to chat
  await page.click('text=Chat');
  
  // Send message
  await page.fill('[placeholder="Type your message..."]', 'Hello, AI!');
  await page.click('button:has-text("Send")');
  
  // Check response
  await expect(page.locator('.message.assistant')).toBeVisible();
});
```

## 🏗️ Architecture Patterns

### Backend Architecture

#### Repository Pattern
```python
# core/db_utils.py
class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, **kwargs) -> Profile:
        profile = Profile(**kwargs)
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
    
    async def get_by_id(self, profile_id: int) -> Optional[Profile]:
        result = await self.session.execute(
            select(Profile).where(Profile.id == profile_id)
        )
        return result.scalar_one_or_none()
```

#### Dependency Injection
```python
# api/routes/profiles.py
from fastapi import Depends
from core.database import get_db
from core.db_utils import ProfileRepository

async def get_profile_repo(db: AsyncSession = Depends(get_db)) -> ProfileRepository:
    return ProfileRepository(db)

@router.post("/profiles")
async def create_profile(
    profile_data: ProfileCreate,
    repo: ProfileRepository = Depends(get_profile_repo)
):
    return await repo.create(**profile_data.dict())
```

#### Provider Pattern
```python
# core/ai_providers.py
class AIProviderManager:
    def __init__(self):
        self.providers = {}
    
    def register_provider(self, name: str, provider: AIProvider):
        self.providers[name] = provider
    
    def get_provider(self, name: str) -> AIProvider:
        if name not in self.providers:
            raise ValueError(f"Provider {name} not found")
        return self.providers[name]
```

### Frontend Architecture

#### Component Structure
```typescript
// components/Chat/ChatInterface.tsx
interface ChatInterfaceProps {
  profileId: number;
  sessionId?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  profileId,
  sessionId
}) => {
  const { messages, sendMessage, isLoading } = useChat(profileId, sessionId);
  const { connect, disconnect, isConnected } = useWebSocket();
  
  return (
    <div className="chat-interface">
      <MessageList messages={messages} />
      <MessageInput onSend={sendMessage} disabled={!isConnected} />
      {isLoading && <TypingIndicator />}
    </div>
  );
};
```

#### Custom Hooks
```typescript
// hooks/useChat.ts
export const useChat = (profileId: number, sessionId?: string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const sendMessage = useCallback(async (content: string) => {
    setIsLoading(true);
    try {
      const response = await api.post('/chat/query', {
        session_id: sessionId,
        profile_id: profileId,
        message: content
      });
      setMessages(prev => [...prev, response.data]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
    }
  }, [profileId, sessionId]);
  
  return { messages, sendMessage, isLoading };
};
```

#### State Management with Zustand
```typescript
// store/chatStore.ts
interface ChatState {
  sessions: ChatSession[];
  currentSession: ChatSession | null;
  messages: Message[];
  addMessage: (message: Message) => void;
  createSession: (profileId: number) => Promise<void>;
}

export const useChatStore = create<ChatState>()((set, get) => ({
  sessions: [],
  currentSession: null,
  messages: [],
  
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),
  
  createSession: async (profileId) => {
    const session = await api.createSession(profileId);
    set((state) => ({ 
      sessions: [...state.sessions, session],
      currentSession: session 
    }));
  },
}));
```

## 🔌 API Development

### Adding New Endpoints

1. **Define Pydantic Models**:
```python
# api/routes/new_feature.py
from pydantic import BaseModel

class NewFeatureRequest(BaseModel):
    name: str
    description: str

class NewFeatureResponse(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
```

2. **Create Repository**:
```python
# core/db_utils.py
class NewFeatureRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, **kwargs) -> NewFeature:
        # Implementation
        pass
```

3. **Add Route**:
```python
# api/routes/new_feature.py
@router.post("/new-feature", response_model=NewFeatureResponse)
async def create_new_feature(
    request: NewFeatureRequest,
    repo: NewFeatureRepository = Depends(get_new_feature_repo)
):
    feature = await repo.create(**request.dict())
    return NewFeatureResponse.from_orm(feature)
```

4. **Include Router**:
```python
# main.py
from api.routes import new_feature
app.include_router(new_feature.router, prefix="/api/v1", tags=["New Feature"])
```

### WebSocket Development
```python
# api/websocket/new_feature.py
@router.websocket("/ws/new-feature")
async def new_feature_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # Process data
            await websocket.send_json({"response": "data"})
    except WebSocketDisconnect:
        pass
```

## 🎨 Frontend Development

### Adding New Components
```typescript
// components/NewFeature/NewFeature.tsx
interface NewFeatureProps {
  onSubmit: (data: NewFeatureData) => void;
  loading?: boolean;
}

export const NewFeature: React.FC<NewFeatureProps> = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState<NewFeatureData>({});
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <Button type="submit" loading={loading}>
        Submit
      </Button>
    </form>
  );
};
```

### Adding New Pages
```typescript
// pages/NewFeaturePage.tsx
import { NewFeature } from '../components/NewFeature/NewFeature';

export const NewFeaturePage: React.FC = () => {
  const handleSubmit = async (data: NewFeatureData) => {
    try {
      await api.createNewFeature(data);
      // Handle success
    } catch (error) {
      // Handle error
    }
  };
  
  return (
    <div className="page">
      <h1>New Feature</h1>
      <NewFeature onSubmit={handleSubmit} />
    </div>
  );
};
```

## 🗄️ Database Development

### Adding New Models
```python
# core/models.py
class NewFeature(Base):
    __tablename__ = "new_features"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Add new feature table"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Migration File Example
```python
# alembic/versions/001_add_new_feature.py
def upgrade():
    op.create_table('new_features',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('new_features')
```

## 🔧 CLI Development

### Adding New Commands
```python
# cli/commands/new_feature.py
import click
from core.database import get_db
from core.db_utils import NewFeatureRepository

@click.group()
def new_feature():
    """Manage new features."""
    pass

@new_feature.command()
@click.argument('name')
@click.option('--description', help='Feature description')
async def create(name, description):
    """Create a new feature."""
    async with get_db() as db:
        repo = NewFeatureRepository(db)
        feature = await repo.create(name=name, description=description)
        click.echo(f"Created feature: {feature.name}")

@new_feature.command()
def list():
    """List all features."""
    # Implementation
    pass
```

```python
# cli/main.py
from .commands.new_feature import new_feature

cli.add_command(new_feature)
```

## 📊 Performance Optimization

### Backend Optimization
```python
# Add caching
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_cached_profile(profile_id: int):
    # Implementation
    pass

# Database query optimization
from sqlalchemy.orm import selectinload

async def get_profile_with_documents(profile_id: int):
    result = await session.execute(
        select(Profile)
        .options(selectinload(Profile.documents))
        .where(Profile.id == profile_id)
    )
    return result.scalar_one_or_none()

# Background tasks
from fastapi import BackgroundTasks

@router.post("/process-document")
async def process_document(
    background_tasks: BackgroundTasks,
    document_id: str
):
    background_tasks.add_task(process_document_task, document_id)
    return {"status": "processing"}
```

### Frontend Optimization
```typescript
// React.memo for component optimization
export const ExpensiveComponent = React.memo<Props>(({ data }) => {
  return <div>{/* Component content */}</div>;
});

// useMemo for expensive calculations
const expensiveValue = useMemo(() => {
  return expensiveCalculation(data);
}, [data]);

// useCallback for function memoization
const handleClick = useCallback((id: string) => {
  onClick(id);
}, [onClick]);

// Code splitting
const LazyComponent = lazy(() => import('./LazyComponent'));

// Virtual scrolling for large lists
import { FixedSizeList as List } from 'react-window';
```

## 🚀 Deployment Considerations

### Environment-Specific Configuration
```python
# config/settings.py
class Settings(BaseSettings):
    environment: str = "development"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
```

### Health Checks
```python
# api/routes/health.py
@router.get("/health/detailed")
async def detailed_health():
    checks = {
        "database": await check_database_health(),
        "ai_providers": await check_ai_providers_health(),
        "storage": await check_storage_health(),
    }
    
    overall_status = "healthy" if all(checks.values()) else "degraded"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": datetime.utcnow()
    }
```

## 📝 Documentation

### Code Documentation
```python
def process_document(document_id: str, profile_id: int) -> ProcessingResult:
    """
    Process a document for a specific profile.
    
    Args:
        document_id: Unique identifier for the document
        profile_id: Profile to associate the document with
        
    Returns:
        ProcessingResult containing status and metadata
        
    Raises:
        DocumentNotFoundError: If document doesn't exist
        ProcessingError: If processing fails
    """
    pass
```

### API Documentation
```python
@router.post(
    "/profiles",
    response_model=ProfileResponse,
    status_code=201,
    summary="Create a new AI profile",
    description="Creates a new AI profile with the specified configuration.",
    responses={
        201: {"description": "Profile created successfully"},
        400: {"description": "Invalid profile data"},
        409: {"description": "Profile with this name already exists"}
    }
)
async def create_profile(profile_data: ProfileCreate):
    pass
```

## 🤝 Contributing Guidelines

### Pull Request Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation
6. Submit pull request

### Code Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Security considerations addressed
- [ ] Performance impact considered

### Release Process
```bash
# Version bump
bump2version patch  # or minor, major

# Create release
git tag v1.0.0
git push origin v1.0.0

# Deploy to staging
docker-compose -f docker-compose.staging.yml up -d

# Deploy to production (after testing)
docker-compose -f docker-compose.prod.yml up -d
```

---

**Happy Coding!** 🚀 This development guide should help you contribute effectively to the RAG application.
