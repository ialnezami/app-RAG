#!/usr/bin/env python3
"""
RAG Application CLI Launcher

This script provides easy access to the CLI tools.
"""

import sys
import os
from pathlib import Path

# Add the CLI directory to the Python path
cli_dir = Path(__file__).parent / 'cli'
sys.path.insert(0, str(cli_dir))

# Import and run the main CLI
if __name__ == '__main__':
    from main import main
    main()
