# Phase 5: CLI Tools

**Phase:** 5  
**Status:** Completed  
**Priority:** Medium  
**Estimated Duration:** 1-2 weeks  
**Dependencies:** Phase 3 (Backend Development)

## Overview
Develop comprehensive CLI tools for system management, document ingestion, profile management, and configuration.

## Tasks

### 5.1 CLI Structure
- [x] Create cli/main.py (CLI entry point)
- [x] Set up cli/commands/ directory
- [x] Create commands/init.py (database initialization)
- [x] Create commands/ingest.py (document ingestion)
- [x] Create commands/profiles.py (profile management)
- [x] Create commands/reset.py (data reset commands)
- [x] Set up cli/utils/ directory
- [x] Create utils/file_processing.py

### 5.2 CLI Commands Implementation
- [x] Implement init-db command
- [x] Implement init-profiles command
- [x] Implement status command
- [x] Implement profiles list/create/update/delete commands
- [x] Implement ingest command (single file)
- [x] Implement ingest-folder command (recursive)
- [x] Implement documents list/delete commands
- [x] Implement reset-profile/reset-all commands
- [x] Implement config validate/test-providers commands

## CLI Commands Reference

### Installation & Setup
```bash
# Initialize database
python cli.py init-db

# Create default profiles
python cli.py init-profiles

# Check system status
python cli.py status
```

### Profile Management
```bash
# List profiles
python cli.py profiles list

# Create profile
python cli.py profiles create "Technical Expert" --provider anthropic --model claude-3-sonnet

# Update profile
python cli.py profiles update 1 --prompt "New prompt here"

# Delete profile
python cli.py profiles delete 2
```

### Document Management
```bash
# Ingest single file
python cli.py ingest 1 document.pdf

# Ingest folder
python cli.py ingest-folder 1 ./documents/ --recursive

# List documents
python cli.py documents list --profile 1

# Delete document
python cli.py documents delete doc-uuid-here

# Reset profile data
python cli.py reset-profile 1

# Reset all data
python cli.py reset-all
```

### Configuration
```bash
# Validate config
python cli.py config validate

# Test AI providers
python cli.py config test-providers

# Update provider settings
python cli.py config update-provider openai --base-url "https://custom.openai.com/v1"
```

## Features

### Core Functionality
- Database initialization and management
- Profile creation and configuration
- Document ingestion (single files and folders)
- System status monitoring
- Configuration validation
- Data reset capabilities

### Advanced Features
- Recursive folder processing
- Batch operations
- Progress indicators
- Error handling and reporting
- Configuration management
- Provider testing

## Deliverables
- Complete CLI application
- All commands implemented
- Comprehensive help system
- Error handling and validation
- Progress indicators
- Configuration management

## Success Criteria
- All CLI commands work correctly
- Help system is comprehensive
- Error handling is robust
- Commands are intuitive to use
- Performance is acceptable
- Documentation is clear

## Notes
The CLI tools are essential for system administration and bulk operations. Ensure they are reliable and well-documented for users who prefer command-line interfaces.
