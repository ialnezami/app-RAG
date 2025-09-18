# 👤 User Guide

## Full-Stack RAG Application User Guide

Welcome to your RAG (Retrieval-Augmented Generation) application! This guide will help you get the most out of your AI-powered document assistant.

## 🚀 Getting Started

### First Steps
1. **Access the Application**: Open http://localhost:3000 in your browser
2. **Check System Status**: Verify all services are running (green indicators)
3. **Create Your First Profile**: Set up an AI assistant personality
4. **Upload Documents**: Add documents for the AI to reference
5. **Start Chatting**: Ask questions about your documents

## 🎭 Managing AI Profiles

AI Profiles define how your assistant behaves and which AI model it uses.

### Creating a Profile
1. Navigate to **Profiles** in the sidebar
2. Click **"Create New Profile"**
3. Fill in the details:
   - **Name**: Give your profile a descriptive name
   - **Description**: Brief explanation of the profile's purpose
   - **AI Provider**: Choose from OpenAI, Anthropic, Google, or custom
   - **Model**: Select the specific AI model
   - **System Prompt**: Define how the AI should behave
   - **Settings**: Configure advanced options

### Example Profiles

#### General Assistant
```
Name: General Helper
Provider: OpenAI
Model: gpt-4o-mini
Prompt: You are a helpful assistant. Answer questions clearly and concisely using the provided context.
```

#### Technical Expert
```
Name: Code Reviewer
Provider: Anthropic
Model: claude-3-sonnet
Prompt: You are a senior software engineer. Provide detailed technical explanations and code reviews based on the documentation.
```

#### Creative Writer
```
Name: Writing Assistant
Provider: OpenAI
Model: gpt-4
Prompt: You are a creative writing assistant. Help with storytelling, character development, and narrative structure using the provided materials.
```

### Profile Settings
- **Max Context Chunks**: How many document sections to include (1-20)
- **Chunk Size**: Size of each text section (500-2000 characters)
- **Chunk Overlap**: Overlap between sections (50-500 characters)
- **Temperature**: Creativity level (0.0-1.0)
- **Max Tokens**: Maximum response length

## 📄 Document Management

### Supported File Types
- **PDF**: Text-based PDFs (not scanned images)
- **DOCX**: Microsoft Word documents
- **TXT**: Plain text files
- **MD**: Markdown files

### Uploading Documents
1. Go to **Documents** section
2. Click **"Upload Document"**
3. Select your file (max 10MB)
4. Choose the profile to associate with
5. Wait for processing to complete

### Document Processing
When you upload a document:
1. **Text Extraction**: Content is extracted from the file
2. **Text Chunking**: Content is split into manageable sections
3. **Embedding Generation**: AI creates vector representations
4. **Storage**: Chunks are stored with embeddings for search

### Processing Status
- **⏳ Uploading**: File is being uploaded
- **🔄 Processing**: Text extraction and embedding generation
- **✅ Complete**: Ready for chat and search
- **❌ Failed**: Processing encountered an error

### Managing Documents
- **View Details**: Click on any document to see metadata
- **Reprocess**: Re-run processing if needed
- **Delete**: Remove document and all associated data
- **Search**: Find specific content across documents

## 💬 Chat Interface

### Starting a Chat
1. Navigate to **Chat** section
2. Select an AI profile from the dropdown
3. Choose **"New Chat"** or continue an existing session
4. Start typing your questions

### Chat Features

#### Real-time Responses
- Messages appear as the AI generates them
- Typing indicators show when AI is working
- Context sources are highlighted

#### Context Sources
Each AI response shows which document sections were used:
- **Document name**: Source file
- **Similarity score**: How relevant the section is
- **Preview**: Snippet of the referenced text
- **Click to expand**: See full context

#### Message Types
- **👤 User**: Your questions and messages
- **🤖 Assistant**: AI responses with context
- **📎 System**: Status updates and notifications

### Best Practices for Questions

#### Effective Questions
✅ **Good**: "What are the main benefits of machine learning mentioned in the research paper?"
✅ **Good**: "How does the authentication system work according to the technical documentation?"
✅ **Good**: "Summarize the key findings from the financial report."

#### Less Effective Questions
❌ **Avoid**: "Hi" or "Hello" (too generic)
❌ **Avoid**: "What's in the document?" (too broad)
❌ **Avoid**: Questions about information not in your documents

#### Question Types That Work Well
- **Summarization**: "Summarize the main points of..."
- **Explanation**: "How does X work according to..."
- **Comparison**: "What's the difference between X and Y in..."
- **Extraction**: "What are the requirements listed in..."
- **Analysis**: "What are the pros and cons of..."

### Chat Management
- **Session History**: All your conversations are saved
- **Session Names**: Rename chats for easy organization
- **Search History**: Find past conversations
- **Export Chat**: Download conversation history
- **Delete Sessions**: Remove unwanted conversations

## 🔍 Search Functionality

### Document Search
Find specific information across all your documents:

1. Go to **Documents** section
2. Use the search bar at the top
3. Enter keywords or phrases
4. Review results with similarity scores
5. Click results to see full context

### Search Tips
- **Specific terms**: Search for exact phrases in quotes
- **Concepts**: Search for ideas, not just exact words
- **Multiple terms**: Use several related keywords
- **Context matters**: Results show surrounding text

### Search Results
Each result shows:
- **Relevance Score**: How well it matches your query
- **Document Source**: Which file contains the information
- **Context Preview**: Surrounding text for context
- **Direct Access**: Jump to chat with this context

## ⚙️ Settings and Configuration

### Application Settings
Access settings through the **Settings** page:

#### Display Options
- **Theme**: Light or dark mode
- **Language**: Interface language
- **Timezone**: Local timezone for timestamps

#### Chat Settings
- **Auto-save**: Automatically save conversations
- **Context Preview**: Show/hide context sources
- **Typing Indicators**: Enable/disable typing animations
- **Sound Notifications**: Audio alerts for new messages

#### File Upload Settings
- **Auto-process**: Automatically process uploaded files
- **Notification**: Alert when processing completes
- **Backup**: Keep original files

### Profile Management
- **Default Profile**: Set which profile to use by default
- **Profile Switching**: Quick switch between profiles
- **Profile Backup**: Export/import profile configurations

## 🛠️ Troubleshooting

### Common Issues

#### Documents Not Processing
**Problem**: Document stuck in "Processing" state
**Solutions**:
1. Check file format is supported
2. Ensure file isn't corrupted
3. Try re-uploading the document
4. Check system status for errors

#### AI Not Responding
**Problem**: Chat messages not getting responses
**Solutions**:
1. Verify API keys are configured
2. Check internet connection
3. Try a different AI profile
4. Check system status

#### Poor Search Results
**Problem**: Search doesn't find relevant information
**Solutions**:
1. Try different keywords or phrases
2. Check if documents are fully processed
3. Verify documents contain the information you're seeking
4. Try more specific or more general search terms

#### Slow Performance
**Problem**: Application running slowly
**Solutions**:
1. Check system resources (CPU, memory)
2. Reduce number of context chunks in profile settings
3. Close unused browser tabs
4. Restart the application if needed

### Getting Help
1. **Check Status**: Visit the status page for system health
2. **Review Logs**: Check browser console for errors
3. **Restart Services**: Try refreshing the page
4. **Check Documentation**: Review setup and API guides

## 📊 Understanding Your Data

### Privacy and Security
- **Local Storage**: All data stays on your system
- **No External Sharing**: Documents aren't sent to third parties
- **API Keys**: Only used for AI provider communication
- **Encryption**: Sensitive data is encrypted

### Data Organization
- **Profiles**: Separate workspaces for different use cases
- **Sessions**: Organized conversation history
- **Documents**: Centralized file management
- **Search History**: Track your queries and results

### Backup and Export
- **Chat Export**: Download conversation history
- **Document Backup**: Keep copies of original files
- **Profile Export**: Save profile configurations
- **Settings Backup**: Export application settings

## 🎯 Use Cases and Examples

### Research Assistant
**Setup**: Create a "Research Assistant" profile with academic prompt
**Documents**: Upload research papers, articles, studies
**Usage**: Ask for summaries, comparisons, methodology explanations

### Technical Documentation
**Setup**: Create a "Technical Expert" profile
**Documents**: Upload API docs, user manuals, technical specifications
**Usage**: Get implementation details, troubleshooting help, code examples

### Legal Document Review
**Setup**: Create a "Legal Assistant" profile
**Documents**: Upload contracts, policies, legal documents
**Usage**: Extract key terms, identify risks, summarize obligations

### Creative Writing
**Setup**: Create a "Writing Assistant" profile
**Documents**: Upload reference materials, style guides, examples
**Usage**: Get writing suggestions, style feedback, creative ideas

### Business Analysis
**Setup**: Create a "Business Analyst" profile
**Documents**: Upload reports, financial statements, market research
**Usage**: Analyze trends, extract insights, create summaries

## 🚀 Advanced Features

### Custom AI Providers
Add your own AI endpoints:
1. Edit `backend/config/config.json`
2. Add custom provider configuration
3. Restart the application
4. Create profiles using custom provider

### API Integration
Use the REST API for automation:
- Bulk document upload
- Automated processing
- Programmatic chat interactions
- Custom integrations

### Workflow Automation
Create efficient workflows:
1. **Batch Processing**: Upload multiple documents at once
2. **Template Profiles**: Create reusable profile templates
3. **Automated Summaries**: Generate regular document summaries
4. **Integration Scripts**: Connect with other tools

## 📈 Best Practices

### Document Organization
- **Logical Grouping**: Group related documents by profile
- **Descriptive Names**: Use clear, searchable filenames
- **Regular Cleanup**: Remove outdated documents
- **Version Control**: Keep track of document versions

### Profile Management
- **Specific Purposes**: Create profiles for specific use cases
- **Clear Prompts**: Write detailed, specific system prompts
- **Regular Testing**: Test profiles with sample questions
- **Performance Tuning**: Adjust settings based on results

### Efficient Chatting
- **Clear Questions**: Ask specific, well-formed questions
- **Context Awareness**: Reference specific documents when needed
- **Follow-up**: Build on previous responses for deeper insights
- **Session Organization**: Use meaningful session names

### Performance Optimization
- **Appropriate Chunk Sizes**: Balance detail vs. performance
- **Selective Processing**: Only process documents you'll use
- **Regular Maintenance**: Clean up old sessions and documents
- **Monitor Resources**: Watch system performance

---

**Happy Chatting!** 🎉 Your RAG application is ready to help you get insights from your documents.
