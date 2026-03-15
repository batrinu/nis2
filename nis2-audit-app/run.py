#!/usr/bin/env python3
"""
Simple launcher for NIS2 Field Audit Tool.
"""
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.textual_app import main

if __name__ == "__main__":
    main()
