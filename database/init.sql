-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_superuser BOOLEAN DEFAULT FALSE NOT NULL,
    role VARCHAR(50) DEFAULT 'user' NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE,
    CONSTRAINT ck_users_role CHECK (role IN ('admin', 'user', 'guest'))
);

-- Indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_role_active ON users(role, is_active);

-- Profiles table
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    prompt TEXT NOT NULL,
    provider VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    mime_type VARCHAR(100),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    profile_id INTEGER REFERENCES profiles(id) ON DELETE CASCADE,
    metadata JSONB DEFAULT '{}'
);

-- Document chunks table
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    profile_id INTEGER REFERENCES profiles(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat sessions table
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id INTEGER REFERENCES profiles(id) ON DELETE CASCADE,
    session_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    context_chunks JSONB DEFAULT '[]',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_document_chunks_profile ON document_chunks(profile_id);
CREATE INDEX idx_documents_profile ON documents(profile_id);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
CREATE INDEX idx_chat_sessions_profile ON chat_sessions(profile_id);

-- Insert default profiles
INSERT INTO profiles (name, description, prompt, provider, model, settings) VALUES
('General Assistant', 'General purpose Q&A assistant', 'You are a helpful assistant. Use the following context to answer questions accurately.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:', 'openai', 'gpt-4o-mini', '{"max_context_chunks": 5, "chunk_size": 1000, "chunk_overlap": 200}'),
('Technical Expert', 'Technical documentation assistant', 'You are a technical expert. Provide detailed, accurate answers based on the documentation context.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:', 'anthropic', 'claude-3-sonnet', '{"max_context_chunks": 8, "chunk_size": 1500, "chunk_overlap": 300}');
