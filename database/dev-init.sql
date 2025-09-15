-- Development-specific database setup
-- This file is loaded after init.sql in development

-- Create development user with additional permissions
CREATE USER dev_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE rag_db TO dev_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dev_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dev_user;

-- Add development-specific profiles
INSERT INTO profiles (name, description, prompt, provider, model, settings) VALUES
('Development Assistant', 'Development and debugging assistant', 'You are a development assistant. Help with coding, debugging, and technical questions.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:', 'openai', 'gpt-4o-mini', '{"max_context_chunks": 3, "chunk_size": 800, "chunk_overlap": 150}');

-- Enable additional logging for development
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();
