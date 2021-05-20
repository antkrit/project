"""Add project directory to PYTHONPATH if it's not already there"""
import os
import sys

proj_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # level up directory
if proj_dir not in sys.path:  # fix absolute import
    sys.path.append(proj_dir)
